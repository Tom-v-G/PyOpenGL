import numpy as np
import glfw
import glfw.GLFW as GLFW_CONSTANTS
import OpenGL.GL as GL
from OpenGL.GL.shaders import compileProgram, compileShader



def create_shader_program(vertex_filepath: str, geometry_filepath: str | None = None, fragment_filepath: str = "") -> int:

    module_list = [] 

    module_list.append(create_shader_module(vertex_filepath, GL.GL_VERTEX_SHADER))
    if geometry_filepath is not None:
        module_list.append(create_shader_module(geometry_filepath, GL.GL_GEOMETRY_SHADER))
    module_list.append(create_shader_module(fragment_filepath, GL.GL_FRAGMENT_SHADER))

    shader = compileProgram(*module_list)

    for module in module_list:
        GL.glDeleteShader(module)

    return shader


def create_shader_module(filepath: str, module_type: int) -> int:
    source_code = ""
    with open(filepath, "r") as file:
        source_code = file.readlines()
    
    return compileShader(source_code, module_type)

def normalize(v):
    return v / np.linalg.norm(v)

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))