
import ctypes

import freetype
from pyglm import glm
import OpenGL.GL as GL
import numpy as np

from utils import create_shader_program

class HUD():

    def __init__(self, screensize):
        self.characters = self.generate_typeface('fonts/glacial-indifference/GlacialIndifference-Regular.ttf')

        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screensize
        self.projection_matrix = glm.ortho(0., self.SCREEN_WIDTH, 0., self.SCREEN_HEIGHT, -1, 1.)

        filepath = 'shaders/hud'
        self.shader = create_shader_program(vertex_filepath=f"{filepath}/vertex.vert", fragment_filepath=f"{filepath}/fragment.frag")
        self.proj_loc = GL.glGetUniformLocation(self.shader, "projection")
        self.vao, self.vbo = self.generate_buffers()
        
        # Setting up the texture location
        GL.glUseProgram(self.shader)
        # GL.glUniform1i(GL.glGetUniformLocation(self.shader, "text"), 0)
        
        self.textcolor = (1.0, 1.0, 1.0)

    def generate_buffers(self):
        
        VAO = GL.glGenVertexArrays(1)
        VBO = GL.glGenBuffers(1)

        GL.glBindVertexArray(VAO)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, VBO)

        # Allocate buffer (but don't fill it yet)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            6 * 4 * 4,  # 6 vertices * 4 floats * 4 bytes
            None,
            GL.GL_DYNAMIC_DRAW
        )

        # Vertex format: (x, y, u, v)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(
            0,                  # location in shader
            4,                  # vec4
            GL.GL_FLOAT,
            GL.GL_FALSE,
            4 * 4,              # stride (4 floats)
            ctypes.c_void_p(0)
        )

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        return VAO, VBO

    def generate_typeface(self, fontfile):
        typeface = freetype.Face(fontfile)
        typeface.set_pixel_sizes(0, 48)

        characters = {}

        # Only standard printable ascii characters
        for char_code in range(32, 128):
            typeface.load_char(chr(char_code))
            
            bitmap = typeface.glyph.bitmap
            data = np.array(bitmap.buffer, dtype=np.uint8)

            # reshape using pitch, then crop to width
            data = data.reshape(bitmap.rows, bitmap.pitch)[:, :bitmap.width]

            texture = GL.glGenTextures(1)
            GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
            
            GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
            GL.glTexImage2D(
                GL.GL_TEXTURE_2D, #target
                0, # level of detail (0 = base image, otherwise mipmap-level)
                GL.GL_R8, # interal format
                bitmap.width, # width
                bitmap.rows, # height
                0, # border
                GL.GL_RED, # format
                GL.GL_UNSIGNED_BYTE, # type
                data # data
            )   

            # GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
            
            # GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_SWIZZLE_R, GL.GL_ONE)
            # GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_SWIZZLE_G, GL.GL_ONE)
            # GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_SWIZZLE_B, GL.GL_ONE)
            # GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_SWIZZLE_A, GL.GL_RED)

            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

            characters[chr(char_code)] = {
                "texture": texture,
                "size": (bitmap.width, bitmap.rows),
                "bearing": (typeface.glyph.bitmap_left, typeface.glyph.bitmap_top),
                "advance": typeface.glyph.advance.x
            }


        return characters
    
    def render(self, text):
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        GL.glUseProgram(self.shader)
        GL.glUniform1i(GL.glGetUniformLocation(self.shader, "text"), 0)
        GL.glUniform3f(GL.glGetUniformLocation(self.shader, "textColor"), *self.textcolor)
        GL.glUniformMatrix4fv(
            self.proj_loc,
            1,
            GL.GL_FALSE,
            glm.value_ptr(self.projection_matrix)
        )

        GL.glActiveTexture(GL.GL_TEXTURE0)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)

        # Start display in top left corner
        left_x = 50
        x = left_x
        top_y = int(0.92 * self.SCREEN_HEIGHT)
        y = top_y
        scale = 0.75


        for char in text:
            
            if char == '\n':
                x = left_x
                y -= 40
                continue

            ch = self.characters[char]

            xpos = x + ch["bearing"][0] * scale
            ypos = y - (ch["size"][1] - ch["bearing"][1]) * scale

            w = ch["size"][0] * scale
            h = ch["size"][1] * scale

            vertices = np.array([
                xpos,     ypos + h, 0.0, 0.0,
                xpos,     ypos,     0.0, 1.0,
                xpos + w, ypos,     1.0, 1.0,

                xpos,     ypos + h, 0.0, 0.0,
                xpos + w, ypos,     1.0, 1.0,
                xpos + w, ypos + h, 1.0, 0.0,
            ], dtype=np.float32)

            vertices = np.ascontiguousarray(vertices)

            GL.glBindTexture(GL.GL_TEXTURE_2D, ch["texture"])

            GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))

            GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)

            x += (ch["advance"] >> 6) * scale

        GL.glEnable(GL.GL_DEPTH_TEST)