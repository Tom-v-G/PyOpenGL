
import numpy as np

from utils import normalize, clamp


def update_camera_front(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        self.camera_front = normalize(np.array(
            [
                np.cos(np.deg2rad(self.camera_yaw)) * np.cos(np.deg2rad(self.camera_pitch)), # x
                np.sin(np.deg2rad(self.camera_pitch)), # y
                np.sin(np.deg2rad(self.camera_yaw)) * np.cos(np.deg2rad(self.camera_pitch)) # z
            ]
        ))
    return wrapper

class Player():

    def __init__(self, pos): 
        
        self.camera_pos = np.array(pos, dtype=np.float32)
        self.camera_front = np.array([0., 0., -1.], dtype=np.float32)
        self.camera_up = np.array([0., 1., 0.], dtype=np.float32)
        self.camera_yaw = -90.0
        self.camera_pitch = 0.0
        self.movement_speed = 20
        self.looking_speed = 20

    @property
    def camera(self):
        return self.camera_pos, self.camera_front, self.camera_up

    def move_forward(self, delta_time):
        self.camera_pos += delta_time * self.movement_speed * self.camera_front

    def move_backward(self, delta_time):
        self.camera_pos -= delta_time * self.movement_speed * self.camera_front
    
    def move_right(self, delta_time):
        self.camera_pos += delta_time * self.movement_speed * np.cross(self.camera_front, self.camera_up)

    def move_left(self, delta_time):
        self.camera_pos -= delta_time * self.movement_speed * np.cross(self.camera_front, self.camera_up)

    def move_up(self, delta_time):
        self.camera_pos += delta_time * self.movement_speed * self.camera_up

    def move_down(self, delta_time):
        self.camera_pos -= delta_time * self.movement_speed * self.camera_up

    @update_camera_front
    def look_up(self, delta_time):
        self.camera_pitch += delta_time * self.looking_speed * 10
        self.camera_pitch = clamp(self.camera_pitch, -89, 89)

    @update_camera_front
    def look_down(self, delta_time):
        self.camera_pitch -= delta_time * self.looking_speed * 10
        self.camera_pitch = clamp(self.camera_pitch, -89, 89)

    @update_camera_front
    def look_right(self, delta_time):
        self.camera_yaw += delta_time * self.looking_speed * 10

    @update_camera_front
    def look_left(self, delta_time):
        self.camera_yaw -= delta_time * self.looking_speed * 10
    
    @update_camera_front
    def process_rotation(self, delta_time, offset):
        self.camera_yaw += delta_time * self.looking_speed * offset[0]
        self.camera_pitch += delta_time * self.looking_speed * offset[1]
        self.camera_pitch = clamp(self.camera_pitch, -89, 89)