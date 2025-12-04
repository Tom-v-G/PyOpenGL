from config import *

class Plane():

    def __init__(self, 
                 v_1,
                 v_2,
                 v_3,
                 v_4,
                 face_color = 0
                 ): 
        
        self.vertices = np.zeros(4, dtype= data_type_vertex)
        # Quad
        self.vertices[0] = (v_1[0], v_1[1], v_1[2], face_color)
        self.vertices[1] = (v_2[0], v_2[1], v_2[2], face_color)
        self.vertices[2] = (v_3[0], v_3[1], v_3[2], face_color)
        self.vertices[3] = (v_4[0], v_4[1], v_4[2], face_color)

    def triangles(self):
        return int(4)
    
    def build_mesh(self) -> tuple[int, int, int]:

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        print(self.vao)
        print(self.vbo)
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
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, self.triangles())

    def delete(self):
        glDeleteBuffers(1, (self.vbo,))
        glDeleteVertexArrays(1, (self.vao,))


if __name__ == "__main__":

    plane = Plane((0, 0, 0), (1,0, 0), (0, 1, 0), (1, 1, 1), 0)
    print(plane)


