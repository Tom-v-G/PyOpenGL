import numpy as np
import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import sys
sys.path.append(".")
from config import * 
import mesh_factory

class App:
    
    def __init__(self):
        self.initialize_glfw()
        self.initialize_opengl()

    def initialize_glfw(self) -> None:
        glfw.init()
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, 
                         GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GLFW_CONSTANTS.GLFW_TRUE)
        
        self.window = glfw.create_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Test1", None, None)
        glfw.make_context_current(self.window)
        print(glfw.get_current_context())
        print("OpenGL version:", glGetString(GL_VERSION))
        glfw.swap_interval(0) # Vsync
    
    def initialize_opengl(self) -> None:
        glClearColor(0.1, 0.2, 0.4, 1.0)
        # self.triangle_buffers, self.triangle_vao = mesh_factory.build_triangle_mesh()
        # self.triangle_vbo, self.triangle_vao = mesh_factory.build_triangle_mesh_2()
        self.quad_ebo, self.quad_vbo, self.quad_vao = mesh_factory.build_quad_mesh()
        self.shader = create_shader_program("shaders/vertex.txt", "shaders/fragment.txt")

    def run(self):
        curr_time = glfw.get_time()
        frame_count = 0 
        while not glfw.window_should_close(self.window):
            if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS:
                break
            glfw.poll_events()

            c = np.cos(glfw.get_time())
            s = np.sin(glfw.get_time())

            transform = np.array([
                [c, -s, 0, 0],
                [s, c, 0, 0 ],
                [0, 0, 1, 0],
                [0, 0, 0, 1]], dtype=np.float32
            )

            glClear(GL_COLOR_BUFFER_BIT)

            # Specify shader
            glUseProgram(self.shader)
            location = glGetUniformLocation(self.shader, "model")
            glUniformMatrix4fv(
                location,
                1, # amt of matrices
                GL_TRUE, # if Transposed
                transform
            )
            # Specify Mesh
            # glBindVertexArray(self.triangle_vao)
             # Specify draw_method and mesh length
            # glDrawArrays(GL_TRIANGLES, 0, 3)

            glBindVertexArray(self.quad_vbo)
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_BYTE, ctypes.c_void_p(0))
           
            glfw.swap_buffers(self.window)
            
            # Calculate FPS
            new_time = glfw.get_time()
            if new_time - curr_time >= 1.0:
                glfw.set_window_title(self.window, f"FPS: {(frame_count):.0f}")
                frame_count = 0
                curr_time = new_time
            frame_count += 1

    def quit(self):
        # glDeleteBuffers(len(self.triangle_buffers), self.triangle_buffers)
        # glDeleteBuffers(1, (self.triangle_vbo,))
        # glDeleteVertexArrays(1, (self.triangle_vao,))

        glDeleteBuffers(2, (self.quad_ebo, self.quad_vbo))
        glDeleteVertexArrays(1, (self.quad_vao,))
        glDeleteProgram(self.shader)
        glfw.destroy_window(self.window)
        glfw.terminate()

# Pipeline Stages
# Vertex Shader: determines which vertices to draw
# Rasterizer : Interpolates between vertices, works out which points to draw and what their attributes are
# Fragment shader: determines final color of each fragment (pixel)
# Frame buffer

if __name__ == "__main__":
    my_app = App()
    my_app.run()
    my_app.quit()

