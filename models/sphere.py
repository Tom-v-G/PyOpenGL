import sys 

sys.path.append(".")
from config import *

class Sphere():

    def __init__(self, 
                 pos: np.typing.NDArray[np.float32] = np.zeros(shape=(3,), dtype=np.float32),
                 size:int = 1,
                 face_color: int = 0,
                 num_vertices: int = 51
                 ): 
        """
        Docstring for __init__
        
        :param self: Description
        :param pos: Description
        :param size: Description
        :param face_color: Description
        :param num_vertices: Description

        Indices:
        top and bottom consist of l_amt triangles
        middle sections of l_amt quads 
        """
        
        # Class variables
        layer_amt = int(np.floor(np.sqrt(num_vertices - 2)))
        self.layer_amt = layer_amt
        self.vertices = np.zeros(shape=(2 + layer_amt ** 2, 3), dtype=np.float32)
        self.colors = np.zeros(shape=(len(self.vertices)), dtype=np.uint32) + face_color
        self.indices = np.zeros(shape=((2 * layer_amt) + (2 * layer_amt * layer_amt), 3), dtype=np.uint32) # Note: change to uint32 for larger model 
        self.pos =  np.zeros(shape=(3,), dtype=np.float32)
        self.size = 1

        self.vao = None
        self.color_vao = None
        self.vbo = None
        self.ebo = None

        # Fill arrays
        self.fill_vertex_array(layer_amt)
        self.fill_index_array(layer_amt)

        self.update_vertex_array_pos(pos)
        self.update_vertex_array_size(size)


    def update_vertex_array_pos(self, pos: np.typing.NDArray[np.float32]):
        """
        translate the array to (0, 0, 0), add and store new position        
        """
        assert pos.shape == (3,)
        self.vertices = np.add(self.vertices, -self.pos)
        self.pos = pos
        self.vertices = np.add(self.vertices, self.pos)
        
        print(f"v after update: {self.vertices}")
        self.build_mesh() # update the mesh

    def update_vertex_array_size(self, size: float):
        """
        translate the array to (0, 0, 0) and multiply by size        
        """

        self.vertices = np.add(self.vertices, -self.pos)
        self.vertices = self.vertices * size
        self.vertices = np.add(self.vertices, self.pos)
        self.size = size

        self.build_mesh()

    def fill_vertex_array(self, layer_amt: int):
        # Fill vertex array
        # Top
        self.vertices[0] = (0., 1., 0.)
        # Bottom
        self.vertices[-1] = (0., -1., 0.)
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
                    r * np.cos(val), y_val, r * np.sin(val)
                 ) # x, y, z

    def fill_index_array(self, layer_amt: int):
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
            for i in range(layer_amt - 1):
                quads = quad_rows_to_triangles(
                    (layer_1_vertices[i], layer_1_vertices[i + 1]),
                    (layer_2_vertices[i], layer_2_vertices[i + 1]),
                )
                self.indices[layer_amt + (2 * layer * layer_amt) + 2*i] =  quads[0]
                self.indices[layer_amt + (2 * layer * layer_amt) + 2*i + 1] =  quads[1]
            quads = quad_rows_to_triangles(
                (layer_1_vertices[-1], layer_1_vertices[0]),
                (layer_2_vertices[-1], layer_2_vertices[0]),
            )
            self.indices[3 * layer_amt + (2 * layer * layer_amt) -2] = quads[0]
            self.indices[3 * layer_amt + (2* layer * layer_amt) - 1] = quads[1]

    def triangles(self):
        return len(self.vertices)

    def color_mesh(self, vertex_data):
        
        self.color_vertices = vertex_data

        for vertex in self.color_vertices:
            vertex[3] = 1

        if self.color_vao is None:
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
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.color_ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

    def build_mesh(self) -> tuple[int, int, int]:
        
        print("running build mesh")
        # Create combined position and color array
        vertex_data = np.rec.fromarrays([self.vertices[:, 0], self.vertices[:, 1], self.vertices[:, 2], self.colors], shape=(len(self.vertices),), dtype=data_type_vertex)
        print(f"Using vertex data: {vertex_data}")
        print(f"Using indices: {len(self.indices)}")
        # Create and bind buffers
        if self.vao is None:
            print("initiliazing VAO")
            self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        if self.vbo is None:
            self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

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
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        self.color_mesh(vertex_data)

        return (self.ebo, self.vbo, self.vao)

    def render(self):
        glBindVertexArray(self.vao)
        # glDrawArrays(GL_LINE_LOOP, 0, self.triangles())
        # glDrawArrays(GL_TRIANGLE_STRIP, 0, self.triangles())
        glDrawElements(GL_TRIANGLE_STRIP, 3 * len(self.indices) , GL_UNSIGNED_INT,  ctypes.c_void_p(0))
        # glBindVertexArray(self.color_vao)
        # glDrawElements(GL_LINE_LOOP, 3 * len(self.indices) - 1 * self.layer_amt , GL_UNSIGNED_INT,  ctypes.c_void_p(0))

    def delete(self):
        
        glDeleteBuffers(2, (self.vbo, self.ebo))
        glDeleteVertexArrays(1, (self.vao,))


if __name__ == "__main__":

    sphere = Sphere((0,0,0), 1)


