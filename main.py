import numpy as np
import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import time
import sys

from hud import HUD
from input import InputHandler
from math_utils import create_lookat_matrix, create_perspective_matrix
from models.chunk import Chunk
from models.chunk_border import ChunkBorderRenderer
from models.voxel import Voxel
from player import Player
from terraingenerator import TerrainGenerator

sys.path.append(".")
from chunkmanager import ChunkManager
from utils import * 
import mesh_factory
from models import *
from obj_loader import ObjLoader

CHUNK_SIZE = 16
class Model:

    def __init__(self, type, *args, **kwargs):
        if type == "cube":
            self.obj = Voxel(*args, **kwargs)
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

    def __init__(self, SCREEN_SIZE: tuple[int, int]):
        # OpenGL
        self.SCREEN_WIDTH: int = SCREEN_SIZE[0] # Note: overriden by initialize_glfw.
        self.SCREEN_HEIGHT: int = SCREEN_SIZE[1]

        self.window = self.initialize_glfw()
        self.initialize_opengl()

        self.shadergroups = []
        self.player = Player([0., 20., 20.])
        self.terraingenerator = TerrainGenerator(0)
        self.chunkmanager = ChunkManager(self.player, self.terraingenerator)
        self.border_renderer = ChunkBorderRenderer()
        self.input_handler = InputHandler(self.window, self.chunkmanager, self.border_renderer, self.player)
        self.hud = HUD(SCREEN_SIZE)
        self.initialize_models()
        
        self.camera_pos = np.array([0., 20, 20], dtype=np.float32)
        self.camera_front = np.array([0., 0., -1.], dtype=np.float32)
        self.camera_up = np.array([0., 1., 0.], dtype=np.float32)
        self.camera_yaw = -90.0
        self.camera_pitch = 0.0
        self.movement_speed = 20
        self.mouse_sensitivity = 50000
        
        self.last_click = np.array([0.5, 0.5], dtype=np.float32)
        self.mouse_positions = np.array([[0.5, 0.5] for i in range(2)], dtype=np.float32)

        self.current_time = glfw.get_time()
        self.last_frame_time = self.current_time
        self.update_time = self.current_time

        
        # Game variables
        self.EXIT = False


        # TEMP VARIABLES 
        self.x = None

    def initialize_glfw(self) -> None:
        glfw.init()

        monitor = glfw.get_primary_monitor()
        mode = glfw.get_video_mode(monitor)

        glfw.window_hint(GLFW_CONSTANTS.GLFW_DECORATED, GLFW_CONSTANTS.GLFW_FALSE)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, 
                         GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GLFW_CONSTANTS.GLFW_TRUE)
        
        self.SCREEN_WIDTH = mode.size.width
        self.SCREEN_HEIGHT = mode.size.height

        window = glfw.create_window(
            self.SCREEN_WIDTH, 
            self.SCREEN_HEIGHT, 
            "Test1", 
            None, # windowed mode
            # monitor, # fullscreen mode 
            None
        )
        glfw.make_context_current(window)

        print(glfw.get_current_context())
        print("OpenGL version:", glGetString(GL_VERSION))
        print(glGetString(GL_RENDERER))
        print(glGetString(GL_VENDOR))
        glfw.swap_interval(0) # Vsync
        glfw.set_input_mode(window, GLFW_CONSTANTS.GLFW_CURSOR, GLFW_CONSTANTS.GLFW_CURSOR_DISABLED)
        glfw.set_input_mode(window, GLFW_CONSTANTS.GLFW_RAW_MOUSE_MOTION, GLFW_CONSTANTS.GLFW_TRUE)

        return window
    
    def initialize_opengl(self) -> None:
        # GL commands
        glClearColor(0.1, 0.2, 0.4, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_DEPTH_CLAMP)
        glEnable(GL_CULL_FACE)

    def initialize_models(self):
        
        # Default rendering technique
        # standard_shader = ShaderGroup("shaders/standard")
        # standard_shader.add_models(
        #     [
        #         Model("plane", (-1, -1, -1), (-1, -1, 1), (1, -1, -1), (1, -1, 1), 2)
        #     ]
        # )
        
        # self.shadergroups.append(standard_shader)

        # Wireframe mesh rendering
        # voxel_shader = ShaderGroup("shaders/voxel")
        wireframe_shader = ShaderGroup("shaders/wireframe_voxel")
        
        # cube_list = []
        # for x in range(10):
        #     for y in range(10):
        #         for z in range(10):
        #             color = np.random.choice([i for i in range(16)])
        #             cube_list.append(Model("cube", 1, x, y, z, color=color))
        
        
        # chunk_list = []

        # cube_array = [
        #     [ [None for _ in range(16)] for _ in range(16)] for _ in range(16)
        # ]
        # for x in range(16):
        #     for y in range(16):
        #         for z in range(16):
        #             color = np.random.choice([i for i in range(16)])
        #             if y < 9 and np.random.rand() < 0.8:
        #                 cube_array[x][y][z] = color
        #             else :
        #                 cube_array[x][y][z] = None
        
        # self.chunkmanager.add_chunk(Chunk(cube_array, pos_x=0, pos_y=0, pos_z=0))

        # cube_array = [
        #     [ [None for _ in range(16)] for _ in range(16)] for _ in range(16)
        # ]
        # for x in range(16):
        #     for y in range(16):
        #         for z in range(16):
        #             color = np.random.choice([i for i in range(16)])
        #             if x < 6 and np.random.rand() < 0.8:
        #                 cube_array[x][y][z] = color
        #             else :
        #                 cube_array[x][y][z] = None

        # self.chunkmanager.add_chunk(Chunk(cube_array, pos_x=1, pos_y=0, pos_z=0))


        # cube_array = [
        #     [ [None for _ in range(16)] for _ in range(16)] for _ in range(16)
        # ]
        # for x in range(16):
        #     for y in range(16):
        #         for z in range(16):
        #             color = np.random.choice([i for i in range(16)])
        #             if x > 10 and np.random.rand() < 0.8:
        #                 cube_array[x][y][z] = color
        #             else :
        #                 cube_array[x][y][z] = None

        # self.chunkmanager.add_chunk(Chunk(cube_array, pos_x=-1, pos_y=0, pos_z=0))

        # cube_array = [
        #     [ [None for _ in range(16)] for _ in range(16)] for _ in range(16)
        # ]
        # for x in range(16):
        #     for y in range(16):
        #         for z in range(16):
        #             color = np.random.choice([i for i in range(16)])
        #             if y < 4 and np.random.rand() < 0.8:
        #                 cube_array[x][y][z] = color
        #             else :
        #                 cube_array[x][y][z] = None

        # self.chunkmanager.add_chunk(Chunk(cube_array, pos_x=0, pos_y=0, pos_z=1))

        # voxel_shader.add_models(chunk_list)
        # wireframe_shader.add_models(chunk_list)

        # wireframe_shader.add_models(
        #    [Model("sphere", np.array([3., 2., 0.]), 2, 0, num_vertices=1000)]   
        # )

        # self.shadergroups.append(voxel_shader)
        self.shadergroups.append(wireframe_shader)

        # Orbital plane

        v1 = np.array([-2, 1, -1], dtype=np.float32)
        v2 = np.array([-2, -1, -1], dtype=np.float32)
        v3 = np.array([-2, 1, 1], dtype=np.float32)

        # standard_shader = ShaderGroup("shaders/orbital")
        # standard_shader.add_models(
        #     [
        #         Model("plane", v3, (-2, -1, 1), v1, v2,  2)
        #     ]
        # )

        e1 = v2 - v1
        e2 = v3 - v2
        e3 = np.cross(e1, e2)
        self.orbital_transform = np.array([
            [e1[0], e1[1], e1[2]],
            [e2[0], e2[1], e2[2]],
            [e3[0], e3[1], e3[2]]
        ], dtype=np.float32).T

        self.norm_vec = np.array([-1, 0, 0])
        
        # self.shadergroups.append(standard_shader)
 
    def run(self):
        
        fps = 0
        frame_count = 0 

        projection = create_perspective_matrix(1000, 0.1, 90, self.SCREEN_WIDTH / self.SCREEN_HEIGHT)

        while not glfw.window_should_close(self.window):
            
            self.current_time = glfw.get_time()

            # Calculate timedelta        
            delta_time = self.current_time - self.last_frame_time
            self.last_frame_time = self.current_time
            self.input_handler.handle_input(delta_time)

            # Update chunkmanager
            self.chunkmanager.update_renderlist()

            # Calculate FPS
            if self.current_time - self.update_time >= 0.5:
                fps = frame_count
                frame_count = 0
                self.update_time = self.current_time             
            else:
                frame_count += 1

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
            camera_pos, camera_front, camera_up = self.player.camera
            view = create_lookat_matrix(camera_pos, camera_front, camera_up)

            glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            # Render each shader group
            self.chunkmanager.update()
            self.chunkmanager.render(view, projection)
            self.border_renderer.render(self.chunkmanager.renderlist, view, projection)


            x, y, z = self.player.position

            text = f"""FPS: {fps}
x={x:.2f} y={y:.2f} z={z:.2f}
Chunk Coordinates: ({x // CHUNK_SIZE}, {y // CHUNK_SIZE}, {z // CHUNK_SIZE})
Chunks in Memory: {self.chunkmanager.renderlist_size} (renderlist) : {self.chunkmanager.cache_size} (cache) : {self.chunkmanager.chunkdict_size} (chunk dict)
"""

            self.hud.render(text)

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

                # Add orbital transform for orbital shaders
                location = glGetUniformLocation(shader, "u_orbital_transform")
                glUniformMatrix3fv(
                    location,
                    1, # amt of matrices
                    GL_TRUE, # if Transposed
                    self.orbital_transform
                )

                location = glGetUniformLocation(shader, "u_norm_vec")
                glUniform3f(location, self.norm_vec[0], self.norm_vec[1], self.norm_vec[2])

                shadergroup.render()
           
            glfw.swap_buffers(self.window)
            


    def quit(self):
        self.chunkmanager.cleanup()
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

    SCREEN_SIZE = (2560, 1440)
    my_app = App(SCREEN_SIZE)
    my_app.run()
    my_app.quit()

