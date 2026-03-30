import threading
from queue import Queue

import numpy as np
from OpenGL.GL import *

from models.chunk import Chunk
from player import Player
from terraingenerator import TerrainGenerator
from utils import create_shader_program


CHUNK_SIZE  = 16
RENDER_DISTANCE = 3

def manhattan(x_1, x_2):
    return np.sum(np.abs(np.array(x_1) - np.array(x_2)))

# def spherical(x_1, x_2):


class ChunkManager():

    player: Player
    terraingenerator: TerrainGenerator
    chunks: dict[tuple[int, int, int], Chunk]
    renderlist: dict[tuple[int, int, int], Chunk | None]

    def __init__(self, player, terraingenerator):
        self.chunks = {}
        self.player = player
        self.terraingenerator = terraingenerator
        filepath = "shaders/voxel"
        self.shader = create_shader_program(f"{filepath}/vertex.txt", f"{filepath}/geometry.txt", f"{filepath}/fragment.txt")

        self.renderlist, self.last_chunk_pos = self.initialize_renderlist()

        # Multithreading 
        self.load_queue = Queue()
        self.ready_queue = Queue()  # chunks ready to be uploaded to GPU
        self.loader_thread = threading.Thread(target=self._chunk_loader, daemon=True)
        self.loader_thread.start()

        # Create adder and remover 'cubeslice' for each possible movement direction
        self.slice_2d = []

        for i in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            for j in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
                # if manhattan(i, j) < RENDER_DISTANCE:
                self.slice_2d.append((i, j))

    def _chunk_loader(self):
        while True:
            key = self.load_queue.get()
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


    def initialize_renderlist(self):
        
        # convert player position to chunk position
        current_chunk:tuple[int, int, int] = tuple(map(int, self.player.position // CHUNK_SIZE))

        # always render chunk player is in
        renderlist: dict[tuple[int, int, int], Chunk | None] = {} 

        # only render chunks within render distance
        # Cube around player (first sphere around player)
        for x in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            for y in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
                for z in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
                    renderlist[(x + current_chunk[0], y + current_chunk[1], z + current_chunk[2])] = self.get_chunk(x + current_chunk[0], y + current_chunk[1], z + current_chunk[2])

        return renderlist, current_chunk

    def update_renderlist(self):

        # convert player position to chunk position
        current_chunk:tuple[int, int, int] = tuple(map(int, self.player.position // CHUNK_SIZE))

        if current_chunk == self.last_chunk_pos:
            return 
        
        cx, cy, cz = current_chunk

        new_keys = set(
            (cx + dx, cy + dy, cz + dz)
            for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1)
            for dy in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1)
            for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1)
        )

        current_keys = set(self.renderlist.keys())

        for key in current_keys - new_keys:
            self.renderlist.pop(key)
        for key in new_keys - current_keys:
            self.renderlist[key] = self.get_chunk(*key)  


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

        for position in self.renderlist:
            current_chunk = self.chunks.get(position, None)
            if current_chunk is None:
                self.load_queue.put(position)
                continue
            if not current_chunk.is_built:
                current_chunk.build_mesh()
            current_chunk.render()

    def cleanup(self):
        for chunk in self.chunks.values():
            if chunk is not None:
                chunk.delete()
        self.chunks.clear()
        self.renderlist.clear()

