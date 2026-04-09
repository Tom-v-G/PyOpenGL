import numpy as np
from OpenGL.GL import *
from utils import create_shader_program

CHUNK_SIZE = 16

# 8 corners of a unit cube scaled to CHUNK_SIZE
_VERTICES = np.array([
    [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
    [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],
], dtype=np.float32) * CHUNK_SIZE

# 12 edges as GL_LINES index pairs
_INDICES = np.array([
    0,1, 1,2, 2,3, 3,0,  # bottom face
    4,5, 5,6, 6,7, 7,4,  # top face
    0,4, 1,5, 2,6, 3,7,  # verticals
], dtype=np.uint32)

class ChunkBorderRenderer:

    def __init__(self):
        self.enabled = False
        # Not used atm
        # self.color = (1.0, 1.0, 0.0, 1.0)  # yellow by default

        self.shader = create_shader_program(
            vertex_filepath="shaders/chunkborders/vertex.txt",
            geometry_filepath=None,
            fragment_filepath="shaders/chunkborders/fragment.txt",
        )
        self._uniform_model      = glGetUniformLocation(self.shader, "model")
        self._uniform_view       = glGetUniformLocation(self.shader, "view")
        self._uniform_projection = glGetUniformLocation(self.shader, "projection")
        # self._uniform_color      = glGetUniformLocation(self.shader, "borderColor")

        # Upload the shared box geometry once
        self._vao = glGenVertexArrays(1)
        self._vbo = glGenBuffers(1)
        self._ebo = glGenBuffers(1)

        glBindVertexArray(self._vao)

        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(GL_ARRAY_BUFFER, _VERTICES.nbytes, _VERTICES, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, _INDICES.nbytes, _INDICES, GL_STATIC_DRAW)

        glBindVertexArray(0)

    def render(self, rendered_chunks: set[tuple[int, int, int]], view_matrix, projection_matrix):
        if not self.enabled:
            return

        glUseProgram(self.shader)
        glUniformMatrix4fv(self._uniform_view, 1, GL_TRUE, view_matrix)
        glUniformMatrix4fv(self._uniform_projection, 1, GL_TRUE, projection_matrix)
        # glUniform4f(self._uniform_color, *self.color)

        # Disable depth write so borders draw on top of faces cleanly
        glDepthMask(GL_FALSE)
        glBindVertexArray(self._vao)

        for pos in rendered_chunks:

            # Translate the unit box to this chunk's world position
            model = np.eye(4, dtype=np.float32)
            model[0, 3] = pos[0] * CHUNK_SIZE
            model[1, 3] = pos[1] * CHUNK_SIZE
            model[2, 3] = pos[2] * CHUNK_SIZE
            glUniformMatrix4fv(self._uniform_model, 1, GL_TRUE, model)
            glDrawElements(GL_LINES, len(_INDICES), GL_UNSIGNED_INT, None)

        glBindVertexArray(0)
        glDepthMask(GL_TRUE)

    def cleanup(self):
        glDeleteVertexArrays(1, [self._vao])
        glDeleteBuffers(1, [self._vbo])
        glDeleteBuffers(1, [self._ebo])
        glDeleteProgram(self.shader)