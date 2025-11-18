import numpy as np
import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader



import time
import sys
sys.path.append(".")
from config import * 
import mesh_factory
from cube import Cube

class App:

    def __init__(self, SCREEN_SIZE):
        self.SCREEN_WIDTH = SCREEN_SIZE[0]
        self.SCREEN_HEIGHT = SCREEN_SIZE[1]
        self.initialize_glfw()
        self.initialize_opengl()

    def initialize_glfw(self) -> None:
        glfw.init()
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, 
                         GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GLFW_CONSTANTS.GLFW_TRUE)
        
        self.window = glfw.create_window(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, "Test1", None, None)
        glfw.make_context_current(self.window)
        print(glfw.get_current_context())
        print("OpenGL version:", glGetString(GL_VERSION))
        print(glGetString(GL_RENDERER))
        print(glGetString(GL_VENDOR))
        glfw.swap_interval(0) # Vsync
    
    def initialize_opengl(self) -> None:
        glClearColor(0.1, 0.2, 0.4, 1.0)
        # self.triangle_buffers, self.triangle_vao = mesh_factory.build_triangle_mesh()
        # self.triangle_vbo, self.triangle_vao = mesh_factory.build_triangle_mesh_2()

        self.quad_ebo, self.quad_vbo, self.quad_vao = mesh_factory.build_quad_mesh()
        # self.shader = create_shader_program("shaders/vertex.txt", "shaders/fragment_3.txt")

        cube_obj = Cube(1, 0, 0, 0)
        # self.quad_ebo, self.quad_vbo, self.quad_vao = cube_obj.build_cube_mesh()
        print(f"{self.quad_ebo, self.quad_vbo, self.quad_vao}")
        self.shader = create_shader_program("shaders/vertex.txt", "shaders/fragment.txt")



    def run(self):
        curr_time = glfw.get_time()
        frame_count = 0 

        u_center = np.array([0.5, 0.5], dtype=np.float32)
        toggle = False

        while not glfw.window_should_close(self.window):
            # Check for closing event
            if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS:
                break
            glfw.poll_events()

            # Check for resize
            # NEW_SCREEN_WIDTH, NEW_SCREEN_HEIGHT = glfw.get_window_size(self.window)
            # print(NEW_SCREEN_WIDTH)
            # print(self.SCREEN_WIDTH)
            # if (isinstance(NEW_SCREEN_WIDTH, int) and isinstance(NEW_SCREEN_HEIGHT, int)) and (NEW_SCREEN_WIDTH != self.SCREEN_WIDTH or NEW_SCREEN_HEIGHT != self.SCREEN_HEIGHT):
            #     print('resizing window')
            #     self.SCREEN_WIDTH = NEW_SCREEN_WIDTH
            #     self.SCREEN_HEIGHT = NEW_SCREEN_HEIGHT
            #     self.initialize_opengl()


            if glfw.get_mouse_button(self.window, GLFW_CONSTANTS.GLFW_MOUSE_BUTTON_1) == GLFW_CONSTANTS.GLFW_PRESS:
                toggle = True

            if toggle: 
                u_center = np.array(glfw.get_cursor_pos(self.window), dtype=np.float32)
                u_center[0] = u_center[0] / self.SCREEN_WIDTH
                u_center[1] = 1 - (u_center[1] / self.SCREEN_HEIGHT)
                toggle = False
            
            u_time = glfw.get_time()
            
            # Time dependent Rotation example
            c = np.cos(u_time)
            s = np.sin(u_time)

            transform = np.array([
                [c, -s, 0, 0],
                [s, c, 0, 0 ],
                [0, 0, 1, 0],
                [0, 0, 0, 1]], dtype=np.float32
            )

            transform = np.identity(4, dtype=np.float32)

            glClear(GL_COLOR_BUFFER_BIT)

            # Upload shader
            glUseProgram(self.shader)

            # Specify Transformation matrix
            location = glGetUniformLocation(self.shader, "model") #get location on GPU using name of variable
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

            # Specify Time
            location = glGetUniformLocation(self.shader, "u_time") #get location on GPU using name of variable
            glUniform1f(location, u_time)

            # Specify Screensize
            location = glGetUniformLocation(self.shader, "u_resolution")
            glUniform2f(location, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

            # Add 'center' position for radial shaders 
            location = glGetUniformLocation(self.shader, "u_center")
            glUniform2f(location, u_center[0], u_center[1])

            glBindVertexArray(self.quad_vbo)

            glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_BYTE, ctypes.c_void_p(0))
           
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

    # print(glGetString(GL_RENDERER))
    # print(glGetString(GL_VENDOR))
    
    # print("OpenGL version:", glGetString(GL_VERSION))

    time.sleep(1)
    # temp = input()
    SCREEN_SIZE = [1920, 1080]
    my_app = App(SCREEN_SIZE)
    my_app.run()
    my_app.quit()

