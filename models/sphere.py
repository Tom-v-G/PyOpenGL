import sys 

sys.path.append(".")
from config import *

class Sphere():

    def __init__(self, 
                 pos,
                 size,
                 face_color = 0,
                 num_vertices = 51
                 ): 
        
        # Create vertex and index array
        layer_amt = int(np.floor(np.sqrt(num_vertices - 2)))
        self.vertices = np.zeros(2 + layer_amt ** 2, dtype=data_type_vertex)
        # top and bottom consist of l_amt triangles
        # middle sections of l_amt quads 
        self.indices = np.zeros(shape=((2 * layer_amt) + (2 * layer_amt * layer_amt), 3), dtype=np.ubyte) # Note: change to uint32 for larger models

        # Fill vertex array
        # Top
        self.vertices[0] = (0., 1., 0., face_color)
        # Bottom
        self.vertices[-1] = (0., -1., 0., face_color)
        # Rest
        y_vals = np.flip(np.linspace(-1, 1, layer_amt + 2)) # flip to go from top to bottom
        # print(y_vals[1:-1])
        # radius of inner circle at height y:
        # sin(theta) = y
        # r = cos(arcsin(y))) 
        for y_index, y_val in enumerate(y_vals[1:-1]):
            # layer corresponds to y value
            vals = np.linspace(0, 2*np.pi, layer_amt)
            r = np.cos(np.arcsin(y_val))
            for index, val in enumerate(vals):
                self.vertices[y_index * layer_amt + index + 1] = (
                    r * np.cos(val), y_val, r * np.sin(val), face_color
                ) # x, y, z

        # Fill index array
        # Top 
        for vertex in range(1, layer_amt):
            self.indices[vertex - 1] = (0, vertex, vertex + 1)
        self.indices[layer_amt - 1] = (0, layer_amt, 1)
        # Bottom 
        bottom_vertex_idx =  2 + layer_amt ** 2 - 1
        for vertex in range(1, layer_amt):
            self.indices[(2 * layer_amt * layer_amt) + layer_amt + vertex - 1] = (
                bottom_vertex_idx, # Bottom vertex
                bottom_vertex_idx - layer_amt + vertex,
                bottom_vertex_idx - layer_amt + vertex - 1, # Right hand rule
        )
        self.indices[(2 * layer_amt * layer_amt) + 2 * layer_amt - 1] = (
            bottom_vertex_idx, 
            bottom_vertex_idx - layer_amt,
            bottom_vertex_idx - 1
        )

        def quad_rows_to_triangles(top_row, bottom_row):
            """
             1 -- 2
             |    |
             7 -- 8 

             to (1, 7, 2), (7, 8, 2)
            """
            return (
                (top_row[0], bottom_row[0], top_row[1]), (bottom_row[0], bottom_row[1], top_row[1])
            )

        # Middle Quads
        # God the indexing horror
        for layer in range(layer_amt):
            layer_1_vertices = [(layer * layer_amt + 1) + i for i in range(layer_amt)]
            layer_2_vertices = [((layer + 1) * layer_amt + 1) + i for i in range(layer_amt)]
            # print(layer_1_vertices)
            # print(layer_2_vertices)
            for i in range(layer_amt - 1):
                quads = quad_rows_to_triangles(
                    (layer_1_vertices[i], layer_1_vertices[i + 1]),
                    (layer_2_vertices[i], layer_2_vertices[i + 1]),
                )
                # print(quads)
                self.indices[layer_amt + (2 * layer * layer_amt) + 2*i] =  quads[0]
                self.indices[layer_amt + (2 * layer * layer_amt) + 2*i + 1] =  quads[1]
            quads = quad_rows_to_triangles(
                (layer_1_vertices[-1], layer_1_vertices[0]),
                (layer_2_vertices[-1], layer_2_vertices[0]),
            )
            self.indices[3 * layer_amt + (2 * layer * layer_amt) -2] = quads[0]
            self.indices[3 * layer_amt + (2* layer * layer_amt) - 1] = quads[1]
        # print(self.vertices.shape)
        print(self.vertices)
        print(self.indices)
        print(len(self.indices))
        

    def triangles(self):
        return len(self.vertices)
    

    def color_mesh(self):
        
        self.color_vertices = self.vertices

        for vertex in self.color_vertices:
            vertex[3] = 1

        self.color_vao = glGenVertexArrays(1)
        glBindVertexArray(self.color_vao)

        self.color_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.color_vbo)
        glBufferData(GL_ARRAY_BUFFER, self.color_vertices.nbytes, self.color_vertices, GL_STATIC_DRAW)

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
        self.color_ebo = glGenBuffers(1)
        print(self.ebo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.color_ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

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

        # Element Buffer Object
        self.ebo = glGenBuffers(1)
        print(self.ebo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        self.color_mesh()

        return (self.ebo, self.vbo, self.vao)

    def render(self):
        glBindVertexArray(self.vao)
        # glDrawArrays(GL_LINE_LOOP, 0, self.triangles())
        # glDrawArrays(GL_TRIANGLE_STRIP, 0, self.triangles())
        glDrawElements(GL_TRIANGLE_STRIP, 3 * len(self.indices) , GL_UNSIGNED_BYTE,  ctypes.c_void_p(0))
        glBindVertexArray(self.color_vao)
        glDrawElements(GL_LINE_LOOP, 3 * len(self.indices)  , GL_UNSIGNED_BYTE,  ctypes.c_void_p(0))

    def delete(self):
        
        glDeleteBuffers(2, (self.vbo, self.ebo))
        glDeleteVertexArrays(1, (self.vao,))


if __name__ == "__main__":

    sphere = Sphere((0,0,0), 1)


