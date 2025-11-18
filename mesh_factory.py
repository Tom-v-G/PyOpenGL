from config import *

def build_triangle_mesh() -> tuple[tuple[int], int]:
    
    position_data = np.array(
        (0.75, -0.75, 0.0,
        -0.75, -0.75, 0.0,
        0.0, 0.75, 0.0), dtype = np.float32
    )

    color_data = np.array(
        (0, 1, 2), dtype = np.uint32
    )

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    position_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, position_buffer)

    glBufferData(GL_ARRAY_BUFFER, position_data.nbytes, position_data, GL_STATIC_DRAW)

    # create attribute pointer
    
    attribute_index = 0
    size = 3 # bytes ; length of vector
    stride = 12 # bytes ; amt of data between vertices
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

    # color buffer
    color_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, color_buffer)
    glBufferData(GL_ARRAY_BUFFER, color_data.nbytes, color_data, GL_STATIC_DRAW)

    # create attribute pointer
    attribute_index = 1
    size = 1 # bytes ; length of vector
    stride = 4 # bytes ; amt of data between vertices
    offset = 0 # 
    
    # attrib-I-pointer: integer pointer, no normalization
    glVertexAttribIPointer(
        attribute_index, 
        size, 
        GL_UNSIGNED_INT, # datatype 
        stride, 
        ctypes.c_void_p(offset) # void pointer: raw memory location
    )
    glEnableVertexAttribArray(attribute_index)

    return ((position_buffer, color_buffer), vao)


def build_triangle_mesh_2() -> tuple[int, int]:
    
    vertex_data = np.zeros(3, dtype = data_type_vertex)

    vertex_data[0] = (-0.75, -0.75, 0.0, 0) 
    vertex_data[1] = (0.75, -0.75, 0.0, 1)
    vertex_data[2] = (0.0, 0.75, 0.0, 2)

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)

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

    return (vbo, vao)


def build_quad_mesh() -> tuple[int, int, int]:
    
    vertex_data = np.zeros(4, dtype = data_type_vertex)

    vertex_data[0] = (-0.75, -0.75, 0.0, 0) 
    vertex_data[1] = (0.75, -0.75, 0.0, 1)
    vertex_data[2] = (0.75, 0.75, 0.0, 2)
    vertex_data[3] = (-0.75, 0.75, 0.0, 1)

    index_data = np.array((0, 1, 2, 2, 3, 0), dtype = np.ubyte)

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
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
    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)


    return (ebo, vbo, vao)
