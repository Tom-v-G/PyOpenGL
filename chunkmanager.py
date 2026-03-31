import threading
from queue import PriorityQueue

import numpy as np
from OpenGL.GL import *

from models.chunk import Chunk
from player import Player
from terraingenerator import TerrainGenerator
from utils import create_shader_program


CHUNK_SIZE  = 16
RENDER_DISTANCE = 10

def manhattan(x_1, x_2):
    return np.sum(np.abs(np.array(x_1) - np.array(x_2)))

# def spherical(x_1, x_2):


class ChunkManager():

    player: Player
    terraingenerator: TerrainGenerator
    chunks: dict[tuple[int, int, int], Chunk]
    renderlist: set[tuple[int, int, int]]

    def __init__(self, player, terraingenerator):
        self.chunks = {}
        self.player = player
        self.terraingenerator = terraingenerator
        filepath = "shaders/voxel"
        self.shader = create_shader_program(f"{filepath}/vertex.txt", f"{filepath}/geometry.txt", f"{filepath}/fragment.txt")

        # Multithreading 
        self.loading = set()
        self.load_queue = PriorityQueue()
        self.ready_queue = PriorityQueue()  # chunks ready to be uploaded to GPU

        # Maybe multiple loader threads? 
        # self.loader_thread = threading.Thread(target=self._chunk_loader, daemon=True) 
        # self.loader_thread.start()

        self.loader_threads = [
            threading.Thread(target=self._chunk_loader, daemon=True)
            for _ in range(2)
        ]

        for t in self.loader_threads:
            t.start()

        # Create adder and remover 'cubeslice' for each possible movement direction
        self.slice_2d = [] 
        for i in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1): 
            for j in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1): 
                if manhattan(i, j) < RENDER_DISTANCE: 
                    self.slice_2d.append((i, j))
        
        # 
        self.manhattan_offsets = [
            (dx, dy, dz)
            for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1)
            for dy in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1)
            for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1)
            if abs(dx) + abs(dy) + abs(dz) <= RENDER_DISTANCE
        ]

        self.renderlist = set()
        self.last_chunk_pos = (0, 0, 0)
        self.initialize_renderlist()



    def _chunk_loader(self):
        while True:
            _, _, key = self.load_queue.get()
            cube_array = self.terraingenerator.create_chunk(*key) # Costly call
            chunk = Chunk(cube_array, key)
            self.ready_queue.put((key, chunk))

    def add_chunk(self, chunk: Chunk):
        self.chunks[(chunk.pos_x, chunk.pos_y, chunk.pos_z)] = chunk
    

    def get_chunk(self, pos_x, pos_y, pos_z):
        return self.chunks.get((pos_x, pos_y, pos_z), None)
    

    def remove_chunk(self, pos_x, pos_y, pos_z):
        if (pos_x, pos_y, pos_z) in self.chunks:
            del self.chunks[(pos_x, pos_y, pos_z)]

    def _chunk_priority(self, chunk_pos):
        player_chunk = tuple((self.player.position // CHUNK_SIZE).astype(int))
        
        chunk_delta = np.array(chunk_pos) - np.array(player_chunk)
        
        distance = manhattan(np.zeros(3), chunk_delta)
        direction_bias = -1 * np.inner(self.player.camera_front, chunk_delta)
        return distance + 0.5 * direction_bias

    def initialize_renderlist(self):
        
        # convert player position to chunk position
        current_chunk:tuple[int, int, int] = tuple((self.player.position // CHUNK_SIZE).astype(int))

        # only render chunks within render distance
        # Cube around player (first sphere around player)
        self.renderlist = {
            (current_chunk[0] + dx,
            current_chunk[1] + dy,
            current_chunk[2] + dz)
            for dx, dy, dz in self.manhattan_offsets
        }
        self.last_chunk_pos = current_chunk

    def update_renderlist(self):

        # convert player position to chunk position
        current_chunk:tuple[int, int, int] = tuple((self.player.position // CHUNK_SIZE).astype(int))

        if current_chunk == self.last_chunk_pos:
            return 
        
        cx, cy, cz = current_chunk
        old_cx, old_cy, old_cz = self.last_chunk_pos


        # # Compute movement delta
        # dx = cx - old_cx
        # dy = cy - old_cy
        # dz = cz - old_cz

        # # Only use movement delta update if player has moved a single chunk (for all directions)
        # if abs(dx) == 1 or abs(dy) == 1 or abs(dz) == 1: 
        #     if abs(dx) == 1:
        #         sign = 1 if dx > 0 else -1
        #         remove_x = cx - sign * RENDER_DISTANCE
        #         add_x = cx + sign * RENDER_DISTANCE

        #         for y, z in self.slice_2d:
        #             # Remove old slice
        #             key = (remove_x, old_cy + y, old_cz + z)
        #             self.renderlist.discard(key)

        #             # Add new slice
        #             key = (add_x, cy + y, cz + z)
        #             self.renderlist.add(key)    
        #     if abs(dy) == 1:
        #         sign = 1 if dy > 0 else -1
        #         remove_y = cy - sign * RENDER_DISTANCE
        #         add_y = cy + sign * RENDER_DISTANCE

        #         for x, z in self.slice_2d:
        #             # Remove old slice
        #             key = (old_cx + x, remove_y, old_cz + z)
        #             self.renderlist.discard(key)

        #             # Add new slice
        #             key = (old_cx + x, add_y, old_cz + z)
        #             self.renderlist.add(key)
        #     if abs(dz) == 1:
        #         sign = 1 if dz> 0 else -1
        #         remove_z = cz - sign * RENDER_DISTANCE
        #         add_z = cz + sign * RENDER_DISTANCE

        #         for x, y in self.slice_2d:
        #             # Remove old slice
        #             key = (old_cx + x, old_cy + y, remove_z)
        #             self.renderlist.discard(key)

        #             # Add new slice
        #             key = (old_cx + x, old_cy + y, add_z)
        #             self.renderlist.add(key)


        # otherwise just rebuild renderlist completely
        # else:
        new_renderlist = {
            (cx + dx, cy + dy, cz + dz)
            for dx, dy, dz in self.manhattan_offsets
        }
        self.renderlist = new_renderlist

        # Improvement: remove chunks that are no longer needed:
        # (use a loading list with a larger LOADING_DISTANCE)
        # for key in self.renderlist - new_renderlist:
        #   self.remove_chunk(*key)
        
        self.last_chunk_pos = current_chunk


    def render(self, view_matrix, projection_matrix):
        glUseProgram(self.shader)

        location = glGetUniformLocation(self.shader, "view") #get location on GPU using name of variable
        glUniformMatrix4fv(
            location,
            1, # amt of matrices
            GL_TRUE, # if Transposed
            view_matrix
        )

        # Specify Transformation matrix
        location = glGetUniformLocation(self.shader, "projection") #get location on GPU using name of variable
        glUniformMatrix4fv(
            location,
            1, # amt of matrices
            GL_TRUE, # if Transposed
            projection_matrix
        )

        # get chunks that are ready to be uploaded to GPU
        while not self.ready_queue.empty():
            key, chunk = self.ready_queue.get()
            self.chunks[key] = chunk
            self.loading.discard(key)

        self.counter = 0 # tie breaker for chunks with similar priority 
        for position in self.renderlist:
            current_chunk = self.chunks.get(position, None)
            if current_chunk is None:
                if position not in self.loading:
                    self.loading.add(position)
                    priority = self._chunk_priority(position)
                    self.counter += 1
                    self.load_queue.put((priority, self.counter, position))
                continue
            if not current_chunk.is_uploaded:
                current_chunk.upload_mesh()
            current_chunk.render()
        if self.counter > 9999:
            self.counter = 0

    def cleanup(self):
        for chunk in self.chunks.values():
            if chunk is not None:
                chunk.delete()
        self.chunks.clear()
        self.renderlist.clear()

