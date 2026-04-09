import threading
from enum import Enum, auto
from queue import Queue, PriorityQueue
from collections import deque

import numpy as np
from OpenGL.GL import *

from models.chunk import Chunk
from player import Player
from terraingenerator import TerrainGenerator
from utils import create_shader_program


CHUNK_SIZE  = 16
RENDER_DISTANCE = 5
CHUNK_CACHE_RADIUS = 10
MAX_UPLOADS_PER_FRAME = 4
MAX_DELETES_PER_FRAME = 4
WORKER_THREADS = 4

def manhattan(a, b):
    return int(np.sum(np.abs(np.array(a) - np.array(b))))

# class ChunkState(Enum):
#     LOADING = auto()
#     GENERATED = auto()
#     MESHED = auto()
#     UPLOADED = auto()

class EmptyChunk:
    is_uploaded = True
    def render(self): pass

class ChunkManager():

    player: Player
    terraingenerator: TerrainGenerator
    chunks: dict[tuple[int, int, int], Chunk]
    cache: dict[tuple[int, int, int], Chunk]
    renderlist: set[tuple[int, int, int]]

    def __init__(self, player, terraingenerator):
        self.chunks = {}
        self.cache = {}
        self.player = player

        self.player_chunk: tuple[int, int, int] = (0, 0, 0)
        self.last_chunk_pos: tuple[int, int, int] = (0, 0, 0)

        self.terraingenerator = terraingenerator

        filepath = "shaders/voxel"
        self.shader = create_shader_program(f"{filepath}/vertex.txt", f"{filepath}/geometry.txt", f"{filepath}/fragment.txt")

        self._uniform_view = glGetUniformLocation(self.shader, "view")
        self._uniform_projection = glGetUniformLocation(self.shader, "projection")
        
        # Multithreading 
        self.loading = set()
        self.load_queue = PriorityQueue()
        self.ready_queue = PriorityQueue()  # chunks ready to be uploaded to GPU
        self.lock = threading.Lock()

        # Multiple loader threads
        self.loader_threads = [
            threading.Thread(target=self._chunk_loader, daemon=True)
            for _ in range(WORKER_THREADS)
        ]

        for t in self.loader_threads:
            t.start()

        
        # list of chunks to check
        self.manhattan_offsets = [
            (dx, dy, dz)
            for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1)
            for dy in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1)
            for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1)
            if abs(dx) + abs(dy) + abs(dz) <= RENDER_DISTANCE
        ]

        #
        # The render volume is a 3D manhattan ball: |dx|+|dy|+|dz| <= R.
        # The face perpendicular to X at dx=±R is the set of (dy,dz) where
        # |dy|+|dz| <= R - |dx| = R - R = 0, i.e. only (0,0).
        # The face at dx=±(R-1) is |dy|+|dz| <= 1, etc.
        # So for each offset k from 0..R, store the 2D slice at distance k from centre.
        #
        # When the player moves +1 in X:
        #   - remove all chunks at x = old_cx - R + k  with slice_at_depth[k], for k in 0..R
        #   - add    all chunks at x = new_cx + R - k  with slice_at_depth[k], for k in 0..R
        #
        # This replaces the previous incorrect single-radius 2D slice.
        self._yz_slices: list[list[tuple[int, int]]] = self._build_face_slices()
        self._xz_slices: list[list[tuple[int, int]]] = self._build_face_slices()
        self._xy_slices: list[list[tuple[int, int]]] = self._build_face_slices()
 
        self._counter = 0
        self.renderlist = set()
        self.initialize_renderlist()

        self.delete_queue = deque() # Needs to be on main thread as it interacts with GPU

    @property
    def cache_size(self):
        return len(self.cache)
    
    @property
    def renderlist_size(self):
        return len(self.renderlist)
    
    @property
    def chunkdict_size(self):
        return len(self.chunks)

    @staticmethod
    def _build_face_slices() -> list[list[tuple[int, int]]]:
        """
        Returns a list of length RENDER_DISTANCE+1.
        Entry k contains all 2D offsets (a, b) with |a|+|b| <= RENDER_DISTANCE - k.
        Used to enumerate the correct face of the manhattan ball at depth k from the edge.
        """
        slices = []
        for k in range(RENDER_DISTANCE + 1):
            radius = RENDER_DISTANCE - k
            slices.append([
                (a, b)
                for a in range(-radius, radius + 1)
                for b in range(-radius + abs(a), radius - abs(a) + 1)
            ])
        return slices
    
    def _player_chunk_pos(self) -> tuple[int, int, int]:
        return tuple((self.player.position // CHUNK_SIZE).astype(int))
 

    def _chunk_priority(self, chunk_pos) -> float:
        
        chunk_delta = np.array(chunk_pos) - np.array(self.player_chunk)
        norm = np.linalg.norm(chunk_delta)
        if norm > 1e-5:
            chunk_dir = chunk_delta / norm
            direction_bias = np.dot(self.player.camera_front, chunk_dir)
        else:
            direction_bias = 0.0
        distance = manhattan(chunk_pos, self.player_chunk)
        return float(distance) - 2.0 * direction_bias


    def _chunk_loader(self):
        while True:
            _, _, key = self.load_queue.get()
            try:
                # TODO add is_empty flag to terraingenerator.
                cube_array = self.terraingenerator.create_chunk(*key)
                chunk = Chunk(cube_array, key)
                self.ready_queue.put((key, chunk))
            finally:
                # FIX: always call task_done so queue.join() works correctly
                self.load_queue.task_done()

    def _in_cache_radius(self, pos):
        return manhattan(pos, self.player_chunk) <= CHUNK_CACHE_RADIUS

    def add_chunk(self, chunk: Chunk):
        self.chunks[(chunk.pos_x, chunk.pos_y, chunk.pos_z)] = chunk
    

    def get_chunk(self, pos_x, pos_y, pos_z):
        return self.chunks.get((pos_x, pos_y, pos_z), None)
    

    def remove_chunk(self, pos_x, pos_y, pos_z):
        if (pos_x, pos_y, pos_z) in self.chunks:
            del self.chunks[(pos_x, pos_y, pos_z)]


    def initialize_renderlist(self):
        self.player_chunk = self._player_chunk_pos()
        cx, cy, cz = self.player_chunk
        self.renderlist = {
            (cx + dx, cy + dy, cz + dz)
            for dx, dy, dz in self.manhattan_offsets
        }
        self.last_chunk_pos = self.player_chunk


    def update_renderlist(self):

        # convert player position to chunk position
        if self.player_chunk  == self.last_chunk_pos:
            return 
        
        cx, cy, cz = self.player_chunk
        old_cx, old_cy, old_cz = self.last_chunk_pos


        # # Compute movement delta
        dx = cx - old_cx
        dy = cy - old_cy
        dz = cz - old_cz

        # # Only use movement delta update if player has moved a single chunk (for all directions)
        if (abs(dx) + abs(dy) + abs(dz)) == 1:
            if abs(dx) == 1:
                sign = 1 if dx > 0 else -1
                for k, slice2d in enumerate(self._yz_slices):
                    depth = RENDER_DISTANCE - k
                    remove_x = cx - sign * depth
                    add_x    = cx + sign * depth
                    for a, b in slice2d:
                        self.renderlist.discard((remove_x, old_cy + a, old_cz + b))
                        self.renderlist.add((add_x, cy + a, cz + b))   

            elif abs(dy) == 1:
                sign = 1 if dy > 0 else -1
                for k, slice2d in enumerate(self._xz_slices):
                    depth = RENDER_DISTANCE - k
                    remove_y = cy - sign * depth
                    add_y    = cy + sign * depth
                    for a, b in slice2d:
                        # FIX: new slice anchored to current position
                        self.renderlist.discard((old_cx + a, remove_y, old_cz + b))
                        self.renderlist.add((cx + a, add_y, cz + b))
 
            elif abs(dz) == 1:
                sign = 1 if dz > 0 else -1
                for k, slice2d in enumerate(self._xy_slices):
                    depth = RENDER_DISTANCE - k
                    remove_z = cz - sign * depth
                    add_z    = cz + sign * depth
                    for a, b in slice2d:
                        # FIX: new slice anchored to current position
                        self.renderlist.discard((old_cx + a, old_cy + b, remove_z))
                        self.renderlist.add((cx + a, cy + b, add_z))


        # otherwise just rebuild renderlist completely
        else:
            self.renderlist = {
                (cx + dx, cy + dy, cz + dz)
                for dx, dy, dz in self.manhattan_offsets
            }

        
        # Clear chunks not in renderlist
        # TODO: use seperate CACHING_DISTANCE
        to_remove = [k for k in self.chunks if k not in self.renderlist]

        
        for key in to_remove:
            chunk = self.chunks[key]

            if self._in_cache_radius(key):
                # move to cache instead of deleting
                self.cache[key] = chunk
            else:
                self.delete_queue.append(chunk)

            del self.chunks[key]
 
        self.last_chunk_pos = self.player_chunk

    def update(self):
        """Update player chunk position and render list. Call once per frame
        before render() so both methods share a consistent player_chunk."""

        self.player_chunk = self._player_chunk_pos()
        self.update_renderlist()

        # update cache
        to_evict = [k for k in self.cache if not self._in_cache_radius(k)]

        for key in to_evict:
            self.delete_queue.append(self.cache[key])
            del self.cache[key]


    def _is_in_frustum(self, chunk_pos: tuple[int, int, int]) -> bool:
        """
        Simple frustum cull: reject the chunk if the vector from player to
        chunk centre points more than ~100° away from camera_front.
        Tune the dot-product threshold to taste (0 = 90°, -0.17 ≈ 100°).
        Skip chunks that are very close so we never cull the chunk we stand in.
        """
        delta = (np.array(chunk_pos) + 0.5) * CHUNK_SIZE - self.player.position
        dist = np.linalg.norm(delta)
        if dist < CHUNK_SIZE * 2:
            return True
        dot = np.dot(self.player.camera_front, delta / dist)
        return dot > -0.17


    def render(self, view_matrix, projection_matrix):
        glUseProgram(self.shader)

        glUniformMatrix4fv(
            self._uniform_view,
            1, # amt of matrices
            GL_TRUE, # if Transposed
            view_matrix
        )

        # Specify Transformation matrix
        glUniformMatrix4fv(
            self._uniform_projection,
            1, # amt of matrices
            GL_TRUE, # if Transposed
            projection_matrix
        )

        # Delete obsolete chunks
        deletes_this_frame = 0
        while self.delete_queue and deletes_this_frame < MAX_DELETES_PER_FRAME:
            chunk = self.delete_queue.popleft()
            chunk.delete()
            deletes_this_frame += 1

        # get chunks that are ready to be uploaded to GPU
        uploads_this_frame = 0
        while not self.ready_queue.empty() and uploads_this_frame < MAX_UPLOADS_PER_FRAME:
            key, chunk = self.ready_queue.get()
            if key in self.renderlist:
                self.chunks[key] = chunk
                with self.lock:
                    self.loading.discard(key)
            else:
                chunk.delete()  # free GPU/CPU memory; don't store it
                with self.lock:
                    self.loading.discard(key)
            self.ready_queue.task_done()
            uploads_this_frame += 1


        for position in sorted(self.renderlist, key=lambda p: manhattan(p, self.player_chunk)):
            
            # Frustum Culling
            if not self._is_in_frustum(position):
                continue

            current_chunk = self.chunks.get(position, None)
            if current_chunk is None:
                
                # Check cache 
                cached = self.cache.pop(position, None)
                if cached is not None:
                    self.chunks[position] = cached
                    continue
                
                # Load chunk
                with self.lock:
                    if position not in self.loading:
                        self.loading.add(position)
                        priority = self._chunk_priority(position)
                        self._counter += 1
                        self.load_queue.put((priority, self._counter, position))
                continue
            if not current_chunk.is_uploaded:
                current_chunk.upload_mesh()
            current_chunk.render()

    def cleanup(self):
        for chunk in self.chunks.values():
            if chunk is not None:
                chunk.delete()
        self.chunks.clear()
        self.renderlist.clear()

