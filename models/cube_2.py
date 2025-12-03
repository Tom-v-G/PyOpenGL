from config import *
class Cube():

    def __init__(self, size, x, y, z): 
        
        color = [0, 0, 0, 1, 1, 1, 2, 2]

        self.vertices = np.zeros(8, dtype= data_type_vertex)

        self.vertices[0] = (x, y, z, color[0])
        self.vertices[1] = (x + size, y, z, color[1])
        self.vertices[2] = (x, y + size, z, color[2])
        self.vertices[3] = (x + size, y + size, z, color[3])
        self.vertices[4] = (x, y, z + size, color[4])
        self.vertices[5] = (x + size, y, z + size, color[5])
        self.vertices[6] = (x, y + size, z + size, color[6])
        self.vertices[7] = (x + size, y + size, z + size, color[7])
    
    def scale(self, scale):
        self.vertices['x'] = scale * self.vertices['x']
        self.vertices['y'] = scale * self.vertices['y']
        self.vertices['z'] = scale * self.vertices['z']

    def __str__(self):
        return f"{self.vertices}"
    
    def build_cube_mesh(self) -> tuple[int, int, int]:

        # Scale 

        # self.scale(0.5)

        # Create 6 quads from vertex data using the vertex indices 
 
        index_data = np.array(
            (
                0, 1, 2, # Front Face
                2, 1, 3, 
                3, 1, 5, # S1
                3, 5, 7,
                4, 5, 7, # Back Face
                4, 7, 6,
                0, 4, 2, # S2
                2, 4, 6, 
                0, 1, 4, # S3
                1, 4, 5,
                2, 3, 6, # S4
                3, 7, 6
             ), dtype = np.ubyte)

        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
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

        # Element Buffer Object
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)


        return (ebo, vbo, vao)



if __name__ == "__main__":

    cube = Cube(1, 0, 0, 0)
    print(cube)
    cube.scale(2)
    print(cube)


