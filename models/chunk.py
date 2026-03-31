
import ctypes

import OpenGL.GL as GL
from utils import *
from models.voxel import Voxel


COLORS = [i for i in range(16)]

data_type_vertex = np.dtype({
    "names": ["x", "y", "z" , "color"],
    "formats": [np.float32, np.float32, np.float32, np.uint32],
    "offsets": [0, 4, 8, 12],
    "itemsize": 16
})

CHUNK_SIZE  = 16

class Chunk():
    """
    Initial chunk size set to 16x16x16 (4096 cubes). 
    """

    def __init__(self, cube_array, position: tuple[int, int, int]): 
        if len(cube_array) != CHUNK_SIZE or len(cube_array[0]) != CHUNK_SIZE or len(cube_array[0][0]) != CHUNK_SIZE:
            raise ValueError("cube_array must be a 16x16x16 array")
        
        self.pos_x, self.pos_y, self.pos_z = position
        
        self.combined_cubes = np.array([], dtype= data_type_vertex)
        self.create_voxel_array(cube_array)
        self.vertex_count = int(len(self.combined_cubes))

        self.vao, self.vbo = None, None
        self.is_uploaded = False


    
    def __del__(self):
        try:
            self.delete()
        except Exception:
            pass


    def create_voxel_array(self, cube_array): 
        
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                for z in range(CHUNK_SIZE):
                    
                    neg_x_active = True
                    pos_x_active = True
                    neg_y_active = True
                    pos_y_active = True
                    neg_z_active = True
                    pos_z_active = True

                    if cube_array[x][y][z] is None:
                        continue
                    
                    if x > 0 and cube_array[x - 1][y][z] is not None:
                        neg_x_active = False

                    if x < CHUNK_SIZE - 1 and cube_array[x + 1][y][z] is not None:
                        pos_x_active = False
                    
                    if y > 0 and cube_array[x][y - 1][z] is not None:
                        neg_y_active = False
                    
                    if y < CHUNK_SIZE - 1 and cube_array[x][y + 1][z] is not None:
                        pos_y_active = False
                        
                    if z > 0 and cube_array[x][y][z - 1] is not None:
                        neg_z_active = False

                    if z < CHUNK_SIZE - 1 and cube_array[x][y][z + 1] is not None:
                        pos_z_active = False

                    self.add_voxel(
                        16 * self.pos_x + x, 
                        16 * self.pos_y + y, 
                        16 * self.pos_z + z, 
                        cube_array[x][y][z], 
                        neg_x_active, 
                        pos_x_active, 
                        neg_y_active, 
                        pos_y_active, 
                        neg_z_active, 
                        pos_z_active
                    )
                    # if cube_array[x][y][z] is not None:
                        # self.add_voxel(16 * self.pos_x + x, 16 * self.pos_y + y, 16 * self.pos_z + z, cube_array[x][y][z])

    def add_voxel(self, x, y, z, color, neg_x_active, pos_x_active, neg_y_active, pos_y_active, neg_z_active, pos_z_active):
        voxel = Voxel(size=1, 
            x=x, 
            y=y, 
            z=z, 
            color=color,
            neg_x_active=neg_x_active,
            pos_x_active=pos_x_active,
            neg_y_active=neg_y_active,
            pos_y_active=pos_y_active,
            neg_z_active=neg_z_active,
            pos_z_active=pos_z_active
        )
        
        self.combined_cubes = np.append(self.combined_cubes, voxel.get_vertices())
        del voxel
    

    def upload_mesh(self) -> None:

        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)

        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.combined_cubes.nbytes, self.combined_cubes, GL.GL_STATIC_DRAW)

        # create attribute pointer
        
        attribute_index = 0
        size = 3 # bytes ; length of vector
        stride = data_type_vertex.itemsize # bytes ; amt of data between vertices
        offset = 0 # 
        
        GL.glVertexAttribPointer(
            attribute_index, 
            size, 
            GL.GL_FLOAT, # datatype 
            GL.GL_FALSE, # normalization
            stride, 
            ctypes.c_void_p(offset) # void pointer: raw memory location
        )
        GL.glEnableVertexAttribArray(attribute_index)
        offset += 12

        # COLOR
        attribute_index = 1
        size = 1 # bytes ; length of vector
        
        # attrib-I-pointer: integer pointer, no normalization
        GL.glVertexAttribIPointer(
            attribute_index, 
            size, 
            GL.GL_UNSIGNED_INT, # datatype 
            stride, 
            ctypes.c_void_p(offset) # void pointer: raw memory location
        )
        GL.glEnableVertexAttribArray(attribute_index)

        self.is_uploaded = True

    def render(self):
        GL.glBindVertexArray(self.vbo)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.vertex_count)

    def delete(self):
        if self.vbo is not None:
            GL.glDeleteBuffers(1, (self.vbo,))
        if self.vao is not None:
            GL.glDeleteVertexArrays(1, (self.vao,))



