
from OpenGL.GL import *

from utils import create_shader_program

class ChunkManager():
    def __init__(self):
        self.chunks = {}
        filepath = "shaders/voxel"
        self.shader = create_shader_program(f"{filepath}/vertex.txt", f"{filepath}/geometry.txt", f"{filepath}/fragment.txt")
        
    def __del__(self):
        for chunk in self.chunks.values():
            del chunk

    def add_chunk(self, chunk):
        self.chunks[(chunk.pos_x, chunk.pos_y, chunk.pos_z)] = chunk
    
    def get_chunk(self, pos_x, pos_y, pos_z):
        return self.chunks.get((pos_x, pos_y, pos_z), None)
    
    def remove_chunk(self, pos_x, pos_y, pos_z):
        if (pos_x, pos_y, pos_z) in self.chunks:
            del self.chunks[(pos_x, pos_y, pos_z)]

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

        for chunk in self.chunks.values():
            chunk.render()


