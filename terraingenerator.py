

import numpy as np

from models.chunk import Chunk


class TerrainGenerator:
    """
    Generates chunks based on seed values.
    """
    def __init__(self, seed, chunkmanager):
        self.seed = seed
        self.chunkmanager = chunkmanager

    def terrain_func(self, x, z):
        return np.floor(6 + 2 * np.cos(0.5 * x +  0.5 * z))
    

    # First generate y - values 
    # Then generate chunks up until y-value 
    # TODO make chunk generation location dependent. 

    def create_chunk(self, x_pos, z_pos):
        
        cube_array: list[list[list[int | None]]] = [
            [ [None for _ in range(16)] for _ in range(16)] for _ in range(16)
        ]

        for x in range(16):
            for z in range(16):
                y_max = int(self.terrain_func(16 * x_pos + x, 16 * z_pos + z))

                for y in range(y_max):
                    cube_array[x][y][z] = y
                    
        self.chunkmanager.add_chunk(Chunk(cube_array, pos_x=x_pos, pos_y=0, pos_z=z_pos))

