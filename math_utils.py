import numpy as np

from utils import normalize


def create_lookat_matrix(camera_pos, camera_front, camera_up):

    # Position vector
    # Target vector 
    # Up vector

    camera_target = camera_pos + camera_front

    # Declarations
    camera_dir = normalize(camera_pos - camera_target)
    camera_right = normalize(np.linalg.cross(camera_up, camera_dir))
    camera_up = normalize(np.linalg.cross(camera_dir, camera_right))
    # camera_up = normalize(camera_up)

    # Axes Matrix
    camera_axes = np.identity(4)
    camera_axes[0:3, 0:3] = np.vstack([camera_right, camera_up, camera_dir])
    
    # Position Matrix
    position = np.identity(4)
    position[0:3, 3] = -1* camera_pos

    # LookAt Matrix
    look_at = np.matmul(camera_axes, position)
    return look_at

def create_perspective_matrix(f, n, fov, aspect_ratio):
    S = 1/ np.tan((np.deg2rad(fov) / 2))
    perspective_matrix = np.array([
        [S, 0, 0, 0],
        [0, S * aspect_ratio, 0, 0],
        [0, 0, -(f + n) / (f - n), -1],
        [0, 0, - (2 * f * n)/(f-n), 0]
    ], dtype=np.float32).T

    return perspective_matrix