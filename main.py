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
from models import *
from obj_loader import ObjLoader

def normalize(v):
    return v / np.linalg.norm(v)

class Model:

    def __init__(self, type, *args, **kwargs):
        if type == "cube":
            self.obj = Cube(*args, **kwargs)
        if type == "plane":
            self.obj = Plane(*args, **kwargs)
        if type == "sphere":
            self.obj = Sphere(*args, **kwargs)
        self.EBO, self.VBO, self.VAO = self.obj.build_mesh()
    
    def render(self):
        self.obj.render()

    def delete(self):
        self.obj.delete()

class ShaderGroup:

    def __init__(self, filepath):
        self.shader = create_shader_program(f"{filepath}/vertex.txt", f"{filepath}/geometry.txt", f"{filepath}/fragment.txt")
        self.models = []
    
    def render(self):
        if not self.models:
            pass
        for model in self.models:
            model.render()
    
    def add_models(self, model_list):
        for model in model_list:
            self.models.append(model)

    def delete(self):
        for model in self.models:
            model.delete() 
        glDeleteProgram(self.shader)
        

class App:

    def __init__(self, SCREEN_SIZE):
        # OpenGL
        self.SCREEN_WIDTH = SCREEN_SIZE[0]
        self.SCREEN_HEIGHT = SCREEN_SIZE[1]

        self.shadergroups = []
        
        self.initialize_glfw()
        self.initialize_opengl()
        self.initialize_models()
        
        self.camera_pos = np.array([0., 0.3, 1], dtype=np.float32)
        self.camera_front = np.array([0., 0., -1.], dtype=np.float32)
        self.camera_up = np.array([0., 1., 0.], dtype=np.float32)
        self.camera_yaw = -90.0
        self.camera_pitch = 0.0
        self.movement_speed = 0.001
        self.mouse_sensitivity = 100

        # Game variables
        self.EXIT = False
        self.last_click = np.array([0.5, 0.5], dtype=np.float32)
        self.mouse_positions = np.array([[0.5, 0.5] for i in range(2)], dtype=np.float32)

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
        # glfw.set_input_mode(self.window, GLFW_CONSTANTS.GLFW_CURSOR, GLFW_CONSTANTS.GLFW_CURSOR_DISABLED) # lock cursor to screen
    
    def initialize_opengl(self) -> None:
        # GL commands
        glClearColor(0.1, 0.2, 0.4, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

    def initialize_models(self):

        # Default rendering technique
        standard_shader = ShaderGroup("shaders/standard")
        standard_shader.add_models(
            [
                Model("plane", (-1, -1, -1), (-1, -1, 1), (1, -1, -1), (1, -1, 1), 2)
            ]
        )
        
        self.shadergroups.append(standard_shader)

        # Wireframe mesh rendering
        wireframe_shader = ShaderGroup("shaders/wireframe")
        cube_amt = 3
        wireframe_shader.add_models(
            [Model("cube", 0.5, i - cube_amt // 2, 0, -3) for i in range(cube_amt)] + [Model("sphere", np.array([3., 2., 0.]), 2, 0, num_vertices=1000)]   
        )

        self.shadergroups.append(wireframe_shader)


    def create_lookat_matrix(self):

        # Position vector
        # Target vector 
        # Up vector

        camera_target = self.camera_pos + self.camera_front

        # Declarations
        camera_dir = normalize(self.camera_pos - camera_target)
        camera_right = normalize(np.linalg.cross(self.camera_up, camera_dir))
        camera_up = normalize(np.linalg.cross(camera_dir, camera_right))

        # Axes Matrix
        camera_axes = np.identity(4)
        camera_axes[0:3, 0:3] = np.vstack([camera_right, camera_up, camera_dir])
        
        # Position Matrix
        position = np.identity(4)
        position[0:3, 3] = -1* self.camera_pos

        # LookAt Matrix
        look_at = np.matmul(camera_axes, position)
        return look_at

    def create_perspective_matrix(self, f, n, fov):
        S = 1/ np.tan((np.deg2rad(fov) / 2))
        perspective_matrix = np.array([
            [S, 0, 0, 0],
            [0, S * (self.SCREEN_WIDTH / self.SCREEN_HEIGHT), 0, 0],
            [0, 0, -(f + n) / (f - n), -1],
            [0, 0, - (2 * f * n)/(f-n), 0]
        ], dtype=np.float32).T

        return perspective_matrix

    def check_input(self):

        # Check for closing event
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS:
            self.EXIT = True
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

        # Check mouse movement
        curr_position = glfw.get_cursor_pos(self.window)
        self.mouse_positions = np.roll(self.mouse_positions, 1, axis=0)
        self.mouse_positions[0] = (curr_position[0] / self.SCREEN_WIDTH, 1 - curr_position[1] / self.SCREEN_HEIGHT)

        # Check mouse press 
        if glfw.get_mouse_button(self.window, GLFW_CONSTANTS.GLFW_MOUSE_BUTTON_1) == GLFW_CONSTANTS.GLFW_PRESS:
            self.last_click = self.mouse_positions[0]

        # Camera Strafing Movement
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_W) == GLFW_CONSTANTS.GLFW_PRESS:
            self.camera_pos += self.movement_speed * self.camera_front
            # self.camera_target[2] -= self.movement_speed
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_S) == GLFW_CONSTANTS.GLFW_PRESS:
            self.camera_pos -= self.movement_speed * self.camera_front
            # self.camera_target[2] += self.movement_speed
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_D) == GLFW_CONSTANTS.GLFW_PRESS:
            self.camera_pos += self.movement_speed * np.cross(self.camera_front, self.camera_up)
            # self.camera_target[0] += self.movement_speed
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_A) == GLFW_CONSTANTS.GLFW_PRESS:
            self.camera_pos -= self.movement_speed * np.cross(self.camera_front, self.camera_up)
            # self.camera_target[0] -= self.movement_speed
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_SPACE) == GLFW_CONSTANTS.GLFW_PRESS:
            self.camera_pos += self.movement_speed * self.camera_up
            # self.camera_target[1] += self.movement_speed
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_LEFT_SHIFT) == GLFW_CONSTANTS.GLFW_PRESS:
            self.camera_pos -= self.movement_speed * self.camera_up
            # self.camera_target[1] -= self.movement_speed

        # # Camera Rotation 
        offset = self.mouse_positions[0] - self.mouse_positions[1]

        self.camera_yaw += self.mouse_sensitivity * offset[0]
        self.camera_pitch += self.mouse_sensitivity * offset[1]

        if self.camera_pitch > 89:
            self.camera_pitch = 89.
        if self.camera_pitch < -89:
            self.camera_pitch = -89.

        self.camera_front = normalize(np.array(
            [
                np.cos(np.deg2rad(self.camera_yaw)) * np.cos(np.deg2rad(self.camera_pitch)), # x
                np.sin(np.deg2rad(self.camera_pitch)), # y
                np.sin(np.deg2rad(self.camera_yaw)) * np.cos(np.deg2rad(self.camera_pitch)) # z
            ]
        ))
        
    def run(self):
        curr_time = glfw.get_time()
        frame_count = 0 

        projection = self.create_perspective_matrix(10, 0.1, 90)
        # projection = np.identity(4)

        single_print = False

        while not glfw.window_should_close(self.window):

            self.check_input()

            if self.EXIT:
                break

            u_time = glfw.get_time()
            
            # Create Model Matrix
            # Time dependent Rotation example

            yaw = np.deg2rad(0)
            # yaw = 0.25 * np.pi
            # yaw = u_time
            pitch = np.deg2rad(0)
            roll = np.deg2rad(0)
            # pitch = u_time
            # roll = np.deg2rad(30)

            yaw_mat = np.array([
                [np.cos(yaw), -np.sin(yaw), 0, 0],
                [np.sin(yaw), np.cos(yaw), 0, 0 ],
                [0, 0, 1, 0],
                [0, 0, 0, 1]], dtype=np.float32
            )
            pitch_mat = np.array([
                [np.cos(pitch), 0, np.sin(pitch), 0],
                [0, 1, 0, 0 ],
                [-np.sin(pitch), 0, np.cos(pitch), 0],
                [0, 0, 0, 1]], dtype=np.float32
            )
            roll_mat = np.array([
                [1, 0, 0, 0],
                [0, np.cos(roll), -np.sin(roll), 0 ],
                [0, np.sin(roll), np.cos(roll), 0],
                [0, 0, 0, 1]], dtype=np.float32
            )
            
            rotation_matrix = np.matmul(yaw_mat, np.matmul(pitch_mat, roll_mat))

            # Create model matrix
            model_mat = np.matmul(np.identity(4), rotation_matrix)
            # model = np.identity(4, dtype=np.float32)

            # Create View Matrix
            view = self.create_lookat_matrix()

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Render each shader group

            # NOTE: this logic should probably be moved to each shadergroup since uniforms might differ between different shaders
            # should probably wait with that until each group is well defined enough to warrent its own class
            for shadergroup in self.shadergroups:

                shader = shadergroup.shader
                glUseProgram(shader)

                location = glGetUniformLocation(shader, "model") #get location on GPU using name of variable
                glUniformMatrix4fv(
                    location,
                    1, # amt of matrices
                    GL_TRUE, # if Transposed
                    model_mat
                )

                location = glGetUniformLocation(shader, "view") #get location on GPU using name of variable
                glUniformMatrix4fv(
                    location,
                    1, # amt of matrices
                    GL_TRUE, # if Transposed
                    view
                )

                # Specify Transformation matrix
                location = glGetUniformLocation(shader, "projection") #get location on GPU using name of variable
                glUniformMatrix4fv(
                    location,
                    1, # amt of matrices
                    GL_TRUE, # if Transposed
                    projection
                )

                # Specify Time
                location = glGetUniformLocation(shader, "u_time") #get location on GPU using name of variable
                glUniform1f(location, u_time)

                # Specify Screensize
                location = glGetUniformLocation(shader, "u_resolution")
                glUniform2f(location, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

                # Add 'center' position for radial shaders 
                location = glGetUniformLocation(shader, "u_center")
                glUniform2f(location, self.last_click[0], self.last_click[1])

                shadergroup.render()
           
            glfw.swap_buffers(self.window)
            
            # Calculate FPS
            new_time = glfw.get_time()
            if new_time - curr_time >= 0.5:
                glfw.set_window_title(self.window, f"FPS: {(frame_count):.0f}")
                frame_count = 0
                curr_time = new_time

                # print(self.camera_yaw)
                # print(self.camera_pitch)
                # print(self.camera_front)                

            frame_count += 1

    def quit(self):
        for shadergroup in self.shadergroups:
            shadergroup.delete()
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

    # time.sleep(1)
    # temp = input()
    SCREEN_SIZE = [1920, 1080]
    my_app = App(SCREEN_SIZE)
    my_app.run()
    my_app.quit()

