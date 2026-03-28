from utils import *

import numpy as np
# COLORS = {
#     'red': 0,
#     'blue': 1,
#     'green': 2,
#     'purple': 3,
#     'orange': 4,
#     'yellow': 5,
#     'brown': 6,
#     'pink': 7,
#     'gray': 8,
#     'deep blue': 9,
#     'light green': 10,
#     'peach': 11,
#     'lavender': 12,
#     'indigo': 13,
#     'coral': 14,
#     'dark green': 15
# }

data_type_vertex = np.dtype({
    "names": ["x", "y", "z" , "color"],
    "formats": [np.float32, np.float32, np.float32, np.uint32],
    "offsets": [0, 4, 8, 12],
    "itemsize": 16
})

COLORS = [i for i in range(16)]

class Voxel():
    
    def __init__(self, 
                size, 
                x, 
                y, 
                z, 
                color = 'green',
                neg_x_active=True,
                pos_x_active=True,
                neg_y_active=True,
                pos_y_active=True,
                neg_z_active=True,
                pos_z_active=True
        ): 
        
        vertices = [] 

        if neg_x_active:
             vertices += [
                (x - size / 2, y - size / 2, z + size / 2, COLORS[color]),
                (x - size / 2, y + size / 2, z + size / 2, COLORS[color]),
                (x - size / 2, y + size / 2, z - size / 2, COLORS[color]),
                (x - size / 2, y - size / 2, z + size / 2, COLORS[color]),
                (x - size / 2, y + size / 2, z - size / 2, COLORS[color]),
                (x - size / 2, y - size / 2, z - size / 2, COLORS[color])
            ]
        if pos_x_active:
            vertices += [
                (x + size / 2, y - size / 2, z - size / 2, COLORS[color]),
                (x + size / 2, y + size / 2, z - size / 2, COLORS[color]),
                (x + size / 2, y - size / 2, z + size / 2, COLORS[color]),
                (x + size / 2, y + size / 2, z - size / 2, COLORS[color]),
                (x + size / 2, y + size / 2, z + size / 2, COLORS[color]),
                (x + size / 2, y - size / 2, z + size / 2, COLORS[color])
            ]
        
        # Bottom Face
        if neg_y_active:
            vertices += [
                (x - size / 2, y - size / 2, z - size / 2, COLORS[color]),
                (x + size / 2, y - size / 2, z - size / 2, COLORS[color]),
                (x - size / 2, y - size / 2, z + size / 2, COLORS[color]),
                (x - size / 2, y - size / 2, z + size / 2, COLORS[color]),
                (x + size / 2, y - size / 2, z - size / 2, COLORS[color]),
                (x + size / 2, y - size / 2, z + size / 2, COLORS[color])
            ]
        
        # Top Face
        if pos_y_active:
            vertices += [
                (x + size / 2, y + size / 2, z + size / 2, COLORS[color]),
                (x + size / 2, y + size / 2, z - size / 2, COLORS[color]),
                (x - size / 2, y + size / 2, z + size / 2, COLORS[color]),
                (x - size / 2, y + size / 2, z + size / 2, COLORS[color]),
                (x + size / 2, y + size / 2, z - size / 2, COLORS[color]),
                (x - size / 2, y + size / 2, z - size / 2, COLORS[color])
            ]

        # Front Face
        if neg_z_active:
            vertices += [
                (x + size / 2, y + size / 2, z - size / 2, COLORS[color]),
                (x + size / 2, y - size / 2, z - size / 2, COLORS[color]),
                (x - size / 2, y + size / 2, z - size / 2, COLORS[color]),
                (x - size / 2, y + size / 2, z - size / 2, COLORS[color]),
                (x + size / 2, y - size / 2, z - size / 2, COLORS[color]),
                (x - size / 2, y - size / 2, z - size / 2, COLORS[color])
            ]

        # Back Face
        if pos_z_active:
            vertices += [
                (x - size / 2, y - size / 2, z + size / 2, COLORS[color]),
                (x + size / 2, y - size / 2, z + size / 2, COLORS[color]),
                (x - size / 2, y + size / 2, z + size / 2, COLORS[color]),
                (x - size / 2, y + size / 2, z + size / 2, COLORS[color]),
                (x + size / 2, y - size / 2, z + size / 2, COLORS[color]),
                (x + size / 2, y + size / 2, z + size / 2, COLORS[color])
            ]
        
        self.vertices = np.array(vertices, dtype=data_type_vertex)


        # self.vertices = np.zeros(36, dtype= data_type_vertex)
        # # Front Face
        # self.vertices[5] = (x - size / 2, y - size / 2, z - size / 2, COLORS[color])
        # self.vertices[4] = (x + size / 2, y - size / 2, z - size / 2, COLORS[color])
        # self.vertices[3] = (x - size / 2, y + size / 2, z - size / 2, COLORS[color])
        # self.vertices[2] = (x - size / 2, y + size / 2, z - size / 2, COLORS[color])
        # self.vertices[1] = (x + size / 2, y - size / 2, z - size / 2, COLORS[color])
        # self.vertices[0] = (x + size / 2, y + size / 2, z - size / 2, COLORS[color])

        # # Left Face 
        # self.vertices[11] = (x - size / 2, y - size / 2, z - size / 2, COLORS[color])
        # self.vertices[10] = (x - size / 2, y + size / 2, z - size / 2, COLORS[color])
        # self.vertices[9] = (x - size / 2, y - size / 2, z + size / 2, COLORS[color])
        # self.vertices[8] = (x - size / 2, y + size / 2, z - size / 2, COLORS[color])
        # self.vertices[7] = (x - size / 2, y + size / 2, z + size / 2, COLORS[color])
        # self.vertices[6] = (x - size / 2, y - size / 2, z + size / 2, COLORS[color])

        # # Right Face 
        # self.vertices[12] = (x + size / 2, y - size / 2, z - size / 2, COLORS[color])
        # self.vertices[13] = (x + size / 2, y + size / 2, z - size / 2, COLORS[color])
        # self.vertices[14] = (x + size / 2, y - size / 2, z + size / 2, COLORS[color])
        # self.vertices[15] = (x + size / 2, y + size / 2, z - size / 2, COLORS[color])
        # self.vertices[16] = (x + size / 2, y + size / 2, z + size / 2, COLORS[color])
        # self.vertices[17] = (x + size / 2, y - size / 2, z + size / 2, COLORS[color])

        # # Top Face
        # self.vertices[23] = (x - size / 2, y + size / 2, z - size / 2, COLORS[color])
        # self.vertices[22] = (x + size / 2, y + size / 2, z - size / 2, COLORS[color])
        # self.vertices[21] = (x - size / 2, y + size / 2, z + size / 2, COLORS[color])
        # self.vertices[20] = (x - size / 2, y + size / 2, z + size / 2, COLORS[color])
        # self.vertices[19] = (x + size / 2, y + size / 2, z - size / 2, COLORS[color])
        # self.vertices[18] = (x + size / 2, y + size / 2, z + size / 2, COLORS[color])

        # # Bottom Face
        # self.vertices[24] = (x - size / 2, y - size / 2, z - size / 2, COLORS[color])
        # self.vertices[25] = (x + size / 2, y - size / 2, z - size / 2, COLORS[color])
        # self.vertices[26] = (x - size / 2, y - size / 2, z + size / 2, COLORS[color])
        # self.vertices[27] = (x - size / 2, y - size / 2, z + size / 2, COLORS[color])
        # self.vertices[28] = (x + size / 2, y - size / 2, z - size / 2, COLORS[color])
        # self.vertices[29] = (x + size / 2, y - size / 2, z + size / 2, COLORS[color])

        # # Back Face
        # self.vertices[30] = (x - size / 2, y - size / 2, z + size / 2, COLORS[color])
        # self.vertices[31] = (x + size / 2, y - size / 2, z + size / 2, COLORS[color])
        # self.vertices[32] = (x - size / 2, y + size / 2, z + size / 2, COLORS[color])
        # self.vertices[33] = (x - size / 2, y + size / 2, z + size / 2, COLORS[color])
        # self.vertices[34] = (x + size / 2, y - size / 2, z + size / 2, COLORS[color])
        # self.vertices[35] = (x + size / 2, y + size / 2, z + size / 2, COLORS[color])

    # def triangles(self):
    #     return int(36)
    
    def get_vertices(self):
        return self.vertices
    
    def build_mesh(self) -> tuple[int, int, int]:

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # create attribute pointer
        
        attribute_index = 0
        size = 3 # number of components (x, y, z)
        stride = data_type_vertex.itemsize # bytes ; amt of data between vertices
        offset = 0 # 
        
        glVertexAttribPointer(
            attribute_index, 
            size, 
            GL_FLOAT, # datatype 
            GL_FALSE, # normalization
            stride, 
            ctypes.c_void_p(offset) # void pointer: raw memory location
        )
        glEnableVertexAttribArray(attribute_index)
        offset += 12 # 3 floats * 4 bytes

        # COLOR
        attribute_index = 1
        size = 1 # bytes ; length of vector
        
        # attrib-I-pointer: integer pointer, no normalization
        glVertexAttribIPointer(
            attribute_index, 
            size, 
            GL_UNSIGNED_INT, # datatype 
            stride, 
            ctypes.c_void_p(offset) # void pointer: raw memory location
        )
        glEnableVertexAttribArray(attribute_index)

        return (None, self.vbo, self.vao)

    def render(self):
        glBindVertexArray(self.vbo)
        glDrawArrays(GL_TRIANGLES, 0, self.triangles())

    def delete(self):
        glDeleteBuffers(1, (self.vbo,))
        glDeleteVertexArrays(1, (self.vao,))


if __name__ == "__main__":

    cube = Voxel(1, 0, 0, 0)
    print(cube)
    cube.scale(2)
    print(cube)


