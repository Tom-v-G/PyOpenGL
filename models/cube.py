from config import *
class Cube():

    def __init__(self, 
                 size, 
                 x, 
                 y, 
                 z, 
                 face_colors=[0, 1, 1, 2, 2, 0]
                 ): 
        
        self.vertices = np.zeros(36, dtype= data_type_vertex)
        # Front Face
        self.vertices[5] = (x - size / 2, y - size / 2, z - size / 2, face_colors[0])
        self.vertices[4] = (x + size / 2, y - size / 2, z - size / 2, face_colors[0])
        self.vertices[3] = (x - size / 2, y + size / 2, z - size / 2, face_colors[0])
        self.vertices[2] = (x - size / 2, y + size / 2, z - size / 2, face_colors[0])
        self.vertices[1] = (x + size / 2, y - size / 2, z - size / 2, face_colors[0])
        self.vertices[0] = (x + size / 2, y + size / 2, z - size / 2, face_colors[0])

        # Left Face 
        self.vertices[11] = (x - size / 2, y - size / 2, z - size / 2, face_colors[1])
        self.vertices[10] = (x - size / 2, y + size / 2, z - size / 2, face_colors[1])
        self.vertices[9] = (x - size / 2, y - size / 2, z + size / 2, face_colors[1])
        self.vertices[8] = (x - size / 2, y + size / 2, z - size / 2, face_colors[1])
        self.vertices[7] = (x - size / 2, y + size / 2, z + size / 2, face_colors[1])
        self.vertices[6] = (x - size / 2, y - size / 2, z + size / 2, face_colors[1])

        # Right Face 
        self.vertices[12] = (x + size / 2, y - size / 2, z - size / 2, face_colors[2])
        self.vertices[13] = (x + size / 2, y + size / 2, z - size / 2, face_colors[2])
        self.vertices[14] = (x + size / 2, y - size / 2, z + size / 2, face_colors[2])
        self.vertices[15] = (x + size / 2, y + size / 2, z - size / 2, face_colors[2])
        self.vertices[16] = (x + size / 2, y + size / 2, z + size / 2, face_colors[2])
        self.vertices[17] = (x + size / 2, y - size / 2, z + size / 2, face_colors[2])

        # Top Face
        self.vertices[23] = (x - size / 2, y + size / 2, z - size / 2, face_colors[3])
        self.vertices[22] = (x + size / 2, y + size / 2, z - size / 2, face_colors[3])
        self.vertices[21] = (x - size / 2, y + size / 2, z + size / 2, face_colors[3])
        self.vertices[20] = (x - size / 2, y + size / 2, z + size / 2, face_colors[3])
        self.vertices[19] = (x + size / 2, y + size / 2, z - size / 2, face_colors[3])
        self.vertices[18] = (x + size / 2, y + size / 2, z + size / 2, face_colors[3])

        # Bottom Face
        self.vertices[24] = (x - size / 2, y - size / 2, z - size / 2, face_colors[4])
        self.vertices[25] = (x + size / 2, y - size / 2, z - size / 2, face_colors[4])
        self.vertices[26] = (x - size / 2, y - size / 2, z + size / 2, face_colors[4])
        self.vertices[27] = (x - size / 2, y - size / 2, z + size / 2, face_colors[4])
        self.vertices[28] = (x + size / 2, y - size / 2, z - size / 2, face_colors[4])
        self.vertices[29] = (x + size / 2, y - size / 2, z + size / 2, face_colors[4])

        # Back Face
        self.vertices[30] = (x - size / 2, y - size / 2, z + size / 2, face_colors[5])
        self.vertices[31] = (x + size / 2, y - size / 2, z + size / 2, face_colors[5])
        self.vertices[32] = (x - size / 2, y + size / 2, z + size / 2, face_colors[5])
        self.vertices[33] = (x - size / 2, y + size / 2, z + size / 2, face_colors[5])
        self.vertices[34] = (x + size / 2, y - size / 2, z + size / 2, face_colors[5])
        self.vertices[35] = (x + size / 2, y + size / 2, z + size / 2, face_colors[5])   

    def triangles(self):
        return int(36)
    
    def build_mesh(self) -> tuple[int, int, int]:

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # create attribute pointer
        
        attribute_index = 0
        size = 3 # bytes ; length of vector
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
        offset += 12

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

    cube = Cube(1, 0, 0, 0)
    print(cube)
    cube.scale(2)
    print(cube)


