import glfw
import ctypes
import numpy as np
from OpenGL.GL import *

# ------------------------
# Vertex data types
# ------------------------
# Vertex: vec3 position + uint color

# temp = input()

data_type_vertex = np.dtype({
    "names": ["x", "y", "z" , "color"],
    "formats": [np.float32, np.float32, np.float32, np.uint32],
    "offsets": [0, 4, 8, 12],
    "itemsize": 16
})

# vertex_list = [ 
#     [1.1, 2.2, 3.3, 5],
#     [4.4, 5.5, 6.6, 7]
# ]

# print(vertex_list)
# print(np.array(vertex_list, dtype=data_type_vertex))


# vertex_array = np.zeros(len(vertex_list), dtype=data_type_vertex)
# for i, v in enumerate(vertex_list):
#     vertex_array[i] = (v[0], v[1], v[2], v[3])

# print(vertex_array)
# print(vertex_array.dtype)
# print(vertex_array['color'].dtype)

# vertex_array = np.array(list(map(tuple, vertex_list)), data_type_vertex)
# print(vertex_array)
# result = np.fromiter(map(tuple, vertex_list), dtype=data_type_vertex)
# print(result)

indices = np.tile(np.array([0, 1, 2, 0, 2, 3], dtype='int'), (6,1))
for face in range(6):
    indices[face] += (face * 4)
indices.shape = (-1,)
print(indices)
# # ------------------------
# # Initialize GLFW
# # ------------------------
# if not glfw.init():
#     raise RuntimeError("GLFW failed to initialize")

# glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
# glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)
# glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

# window = glfw.create_window(800, 600, "Quad Example", None, None)
# if not window:
#     glfw.terminate()
#     raise RuntimeError("GLFW window creation failed")

# glfw.make_context_current(window)

# # ------------------------
# # Quad vertex + index data
# # ------------------------
# vertex_data = np.zeros(4, dtype=data_type_vertex)

# vertex_data[0] = (-0.5, -0.5, 0.0, 0) 
# vertex_data[1] = (0.5, -0.5, 0.0, 1)
# vertex_data[2] = (0.5, 0.5, 0.0, 2)
# vertex_data[3] = (-0.5, 0.5, 0.0, 1)

# index_data = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint8)

# # ------------------------
# # VAO, VBO, EBO
# # ------------------------
# vao = int(glGenVertexArrays(1))
# glBindVertexArray(vao)

# vbo = int(glGenBuffers(1))
# glBindBuffer(GL_ARRAY_BUFFER, vbo)
# glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

# # Position attribute (location = 0)
# glVertexAttribPointer(
#     0,
#     3,
#     GL_FLOAT,
#     GL_FALSE,
#     vertex_data.itemsize,
#     ctypes.c_void_p(0)
# )
# glEnableVertexAttribArray(0)

# # Color attribute (location = 1)
# glVertexAttribIPointer(
#     1,
#     1,
#     GL_UNSIGNED_INT,
#     vertex_data.itemsize,
#     ctypes.c_void_p(12)  # offset: 3 floats * 4 bytes
# )
# glEnableVertexAttribArray(1)

# # EBO
# ebo = int(glGenBuffers(1))
# glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
# glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

# # Unbind VAO (optional)
# glBindVertexArray(0)

# # ------------------------
# # Render loop
# # ------------------------
# while not glfw.window_should_close(window):
#     glfw.poll_events()
#     glClearColor(0.2, 0.3, 0.3, 1.0)
#     glClear(GL_COLOR_BUFFER_BIT)

#     # Bind VAO and draw
#     glBindVertexArray(vao)
#     glDrawElements(GL_TRIANGLES, len(index_data), GL_UNSIGNED_BYTE, None)

#     glfw.swap_buffers(window)

# glfw.terminate()
