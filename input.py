import glfw
import glfw.GLFW as GLFW_CONSTANTS
import numpy as np

from models.chunk import Chunk
from utils import normalize


class InputHandler:
    def __init__(self, window, chunkmanager, player):
        self.window = window
        self.chunkmanager = chunkmanager
        self.player = player

        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = glfw.get_window_size(self.window)

        self.mouse_sensitivity = 20000

        self.last_click = np.array([0.5, 0.5], dtype=np.float32)
        self.mouse_positions = np.array([[0.5, 0.5] for i in range(2)], dtype=np.float32)

        self.x = 3

        self.key_bindings = {
            "move_forward": GLFW_CONSTANTS.GLFW_KEY_W,
            "move_backward": GLFW_CONSTANTS.GLFW_KEY_S,
            "move_right": GLFW_CONSTANTS.GLFW_KEY_D,
            "move_left": GLFW_CONSTANTS.GLFW_KEY_A,
            "move_up": GLFW_CONSTANTS.GLFW_KEY_SPACE,
            "move_down": GLFW_CONSTANTS.GLFW_KEY_LEFT_SHIFT,
            "look_up": GLFW_CONSTANTS.GLFW_KEY_UP,
            "look_down": GLFW_CONSTANTS.GLFW_KEY_DOWN,
            "look_right": GLFW_CONSTANTS.GLFW_KEY_RIGHT,
            "look_left": GLFW_CONSTANTS.GLFW_KEY_LEFT,
            "menu": GLFW_CONSTANTS.GLFW_KEY_ESCAPE,
            "add_chunk": GLFW_CONSTANTS.GLFW_KEY_EQUAL,
            "remove_chunk": GLFW_CONSTANTS.GLFW_KEY_MINUS
        }

        self.prev_keys = {}
        self.update_key_states() # Initialize self.prev_keys with the current key states.


    def is_key_down(self, key):
        return glfw.get_key(self.window, key) == GLFW_CONSTANTS.GLFW_PRESS


    def is_key_pressed(self, key):
        current = self.is_key_down(key)
        previous = self.prev_keys.get(key, False)
        return current and not previous


    def is_key_released(self, key):
        current = self.is_key_down(key)
        previous = self.prev_keys.get(key, False)
        return not current and previous
    

    def update_key_states(self):
        for key in self.key_bindings.values():
            self.prev_keys[key] = self.is_key_down(key)

           

    def handle_input(self, delta_time):

        # Check for closing event
        if self.is_key_down(self.key_bindings["menu"]):
            glfw.set_window_should_close(self.window, True)

        glfw.poll_events()

        # Check mouse movement
        curr_position = glfw.get_cursor_pos(self.window)
        self.mouse_positions = np.roll(self.mouse_positions, 1, axis=0)
        self.mouse_positions[0] = (curr_position[0] / self.SCREEN_WIDTH, 1 - curr_position[1] / self.SCREEN_HEIGHT)

        # Check mouse press 
        if glfw.get_mouse_button(self.window, GLFW_CONSTANTS.GLFW_MOUSE_BUTTON_1) == GLFW_CONSTANTS.GLFW_PRESS:
            self.last_click = self.mouse_positions[0]

        # Player movement and rotation
        if self.is_key_down(self.key_bindings["move_forward"]):
            self.player.move_forward(delta_time)
        if self.is_key_down(self.key_bindings["move_backward"]):
            self.player.move_backward(delta_time)
        if self.is_key_down(self.key_bindings["move_right"]):
            self.player.move_right(delta_time)
        if self.is_key_down(self.key_bindings["move_left"]):
            self.player.move_left(delta_time)
        if self.is_key_down(self.key_bindings["move_up"]):
            self.player.move_up(delta_time)
        if self.is_key_down(self.key_bindings["move_down"]):
            self.player.move_down(delta_time)

        if self.is_key_down(self.key_bindings["look_up"]):
            self.player.look_up(delta_time)
        if self.is_key_down(self.key_bindings["look_down"]):
            self.player.look_down(delta_time)
        if self.is_key_down(self.key_bindings["look_right"]):
            self.player.look_right(delta_time)
        if self.is_key_down(self.key_bindings["look_left"]):
            self.player.look_left(delta_time)

        # # Camera Rotation via mouse movement
        offset = (self.mouse_positions[0] - self.mouse_positions[1]) * self.mouse_sensitivity
        self.player.process_rotation(delta_time, offset)


        # Adding chunks 
        if self.is_key_pressed(self.key_bindings["add_chunk"]):
            
            cube_array = [
                [ [None for _ in range(16)] for _ in range(16)] for _ in range(16)
            ]
            for x in range(16):
                for y in range(16):
                    for z in range(16):
                        color = np.random.choice([i for i in range(16)])
                        if np.random.rand() < 0.8:
                            cube_array[x][y][z] = color
                        else :
                            cube_array[x][y][z] = None

            self.chunkmanager.add_chunk(Chunk(cube_array, pos_x=self.x, pos_y=1, pos_z=0))
            self.x += 1
            print(f"added chunk at x = {self.x - 1}")

        # Removing chunks
        if self.is_key_pressed(self.key_bindings["remove_chunk"]):
            if self.x > 3:
                self.chunkmanager.remove_chunk(self.x - 1, 1, 0)
                print(f"removed chunk at x = {self.x - 1}")
                self.x -= 1
        
        self.update_key_states()
                
