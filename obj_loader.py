from config import *

class ObjLoader():

    def __init__(self, filename):
        vertices = []
        self.normals = []
        self.texcoords = []
        self.indices = []

        color = 1
        for line in open(filename, "r"):
            # Skip comments
            if line.startswith('#'):
                continue
            
            values = line.split()
            # skip empty lines
            if not values:
                continue
            # Vertices
            if values[0] == 'v':
                v = map(float, values[1:4])
                vertices.append([*list(v), int(1)])
            # Normals
            elif values[0] == 'vn':
                v = map(float, values[1:4])
                self.normals.append(list(v))
            # Texture coordinates
            elif values[0] == 'vt':
                v = map(float, values[1:3])
                self.texcoords.append(list(v))
            # Skip material (for now)
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            
            elif values[0] == 'mtllib':
                # self.mtl = MTL(values[1])
                continue
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []

                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                if len(values[1:]) == 4: # Quad face
                    # Split into two triangles 
                    self.indices.append(face[0:3])
                    self.indices.append(face[1:4])
                else:
                    self.indices.append(face)
        
        self.vertices = np.fromiter(map(tuple, vertices), dtype=data_type_vertex, count=len(vertices))
        self.normals = np.array(self.normals, dtype=np.float32)
        self.texcoords = np.array(self.texcoords, dtype=np.float32)
        self.indices = np.array(self.indices, dtype=np.uint32)
             
    def build_mesh(self) -> tuple[int, int, int]:
        
        vao = int(glGenVertexArrays(1))
        glBindVertexArray(vao)

        vbo = int(glGenBuffers(1))
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # create attribute pointer
        
        attribute_index = 0
        size = 3 # bytes ; length of vector
        stride = 16 # bytes ; amt of data between vertices
        offset = 0 # 
        
        glVertexAttribPointer(
            attribute_index, 
            size, 
            GL_FLOAT, # datatype 
            GL_FALSE, # normalization
            stride, 
            ctypes.c_void_p(offset) # void pointer: raw memory location
        )
        glEnableVertexAttribArray(attribute_index)
        offset += 12

        # COLOR
        attribute_index = 1
        size = 1 # bytes ; length of vector
        
        # attrib-I-pointer: integer pointer, no normalization
        glVertexAttribIPointer(
            attribute_index, 
            size, 
            GL_UNSIGNED_INT, # datatype 
            stride, 
            ctypes.c_void_p(offset) # void pointer: raw memory location
        )
        glEnableVertexAttribArray(attribute_index)

        # Element Buffer Object
        ebo = int(glGenBuffers(1))
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)


        return (ebo, vbo, vao)

    def triangles(self):
        return len(self.indices)

if __name__ == "__main__":
    obj = ObjLoader("teapot.obj")  
    # print(f"{obj.vertices=}")              
    print(f"{obj.indices=}")
    print(f"{obj.vertices=}")
    # obj.build_mesh()
                