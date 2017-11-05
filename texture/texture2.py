import sys
from array           import array
from ctypes          import c_void_p
from textwrap        import dedent
from OpenGL.GL       import *
from OpenGL.GLU      import *
from PyQt5.QtOpenGL  import QGLWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui     import QMatrix4x4, QVector3D


class Texture(QGLWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.restart = 0xFFFFFFFF
        self.model = QMatrix4x4()


    def initializeCube(self):

        # compute the normals of the faces
        self.vertices = array('f', [
          # +y face
           0.5, 0.5,  0.5,  # 0
           0.5, 0.5, -0.5,  # 1
          -0.5, 0.5, -0.5,  # 2
          -0.5, 0.5,  0.5,  # 3
          # -y face
           0.5, -0.5,  0.5,  # 4
          -0.5, -0.5,  0.5,  # 5
          -0.5, -0.5, -0.5,  # 6
           0.5, -0.5, -0.5,  # 7
          # top
           0.5,  0.5, 0.5,  # 8
          -0.5,  0.5, 0.5,  # 9
          -0.5, -0.5, 0.5,  # 10
           0.5, -0.5, 0.5,  # 11
          # bottom
          -0.5, -0.5, -0.5,  # 12
          -0.5,  0.5, -0.5,  # 13
           0.5,  0.5, -0.5,  # 14
           0.5, -0.5, -0.5,  # 15
          # +x face
          0.5, -0.5,  0.5,  # 16
          0.5, -0.5, -0.5,  # 17
          0.5,  0.5, -0.5,  # 18
          0.5,  0.5,  0.5,  # 19
          # -x face
          -0.5, -0.5,  0.5,  # 20
          -0.5,  0.5,  0.5,  # 21
          -0.5,  0.5, -0.5,  # 22
          -0.5, -0.5, -0.5   # 23
        ])
        self.colors = array('f', [
          # top
          0,1,0,
          0,1,0,
          0,1,0,
          0,1,0,
          # bottom
          0,.5,0,
          0,.5,0,
          0,.5,0,
          0,.5,0,
          # front
          0,0,1,
          0,0,1,
          0,0,1,
          0,0,1,
          # back
          0,0,.5,
          0,0,.5,
          0,0,.5,
          0,0,.5,
          # right
          1,0,0,
          1,0,0,
          1,0,0,
          1,0,0,
          # left
          .5,0,0,
          .5,0,0,
          .5,0,0,
          .5,0,0
        ])
        self.indices = array('I', [
           0,  1,  2,  3, self.restart,
           4,  5,  6,  7, self.restart,
           8,  9, 10, 11, self.restart,
          12, 13, 14, 15, self.restart,
          16, 17, 18, 19, self.restart,
          20, 21, 22, 23
        ])

        # TODO: create an array of uv coordinates

        # TODO: add texture data here

        # create a new Vertex Array Object on the GPU which saves the attribute
        # layout of our vertices
        self.cubeVao = glGenVertexArrays(1)
        glBindVertexArray(self.cubeVao)

        # create a buffer on the GPU for position and color data
        vertexBuffer, colorBuffer, indexBuffer, uvBuffer = glGenBuffers(4)

        # upload the data to the GPU, storing it in the buffer we just created
        # TODO: upload to uv data to a buffer
        glBindBuffer(GL_ARRAY_BUFFER, vertexBuffer)
        glBufferData(
            GL_ARRAY_BUFFER,
            self.sizeof(self.vertices),
            self.vertices.tostring(),
            GL_STATIC_DRAW
        )
        glBindBuffer(GL_ARRAY_BUFFER, colorBuffer)
        glBufferData(
            GL_ARRAY_BUFFER,
            self.sizeof(self.colors),
            self.colors.tostring(),
            GL_STATIC_DRAW
        )
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indexBuffer)
        glBufferData(
            GL_ELEMENT_ARRAY_BUFFER,
            self.sizeof(self.indices),
            self.indices.tostring(),
            GL_STATIC_DRAW
        )

        # TODO: create a gl texture object
        # TODO: bind to the texture object
        # TODO: load the texture data into the texture object
        # TODO: tell OpenGL how to sample from the texture

        # load our vertex and fragment shaders into a program object on the GPU
        self.cubeProgram = self.loadShaders()
        glUseProgram(self.cubeProgram)

        # bind the attribute "position" (defined in our vertex shader) to the
        # currently bound buffer object, which contains our position data
        # this information is stored in our vertex array object
        # TODO: bind to the "uv" attribute defined in the vertex shader
        glBindBuffer(GL_ARRAY_BUFFER, vertexBuffer)
        position = glGetAttribLocation(self.cubeProgram, 'position')
        glEnableVertexAttribArray(position)
        glVertexAttribPointer(
            position,
            3,
            GL_FLOAT,
            GL_FALSE,
            0,
            c_void_p(0)
        )
        glBindBuffer(GL_ARRAY_BUFFER, colorBuffer)
        color = glGetAttribLocation(self.cubeProgram, 'color')
        glEnableVertexAttribArray(color)
        glVertexAttribPointer(
            color,
            3,
            GL_FLOAT,
            GL_FALSE,
            0,
            c_void_p(0)
        )

        # project, model, and view transformation matrices
        self.cubeProjection = glGetUniformLocation(self.cubeProgram, "projection")


    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glPrimitiveRestartIndex(self.restart)
        glEnable(GL_PRIMITIVE_RESTART)
        self.initializeCube()


    def loadShaders(self):
        # create a GL Program Object
        program = glCreateProgram()

        # vertex shader
        # TODO: add a vec2 input uv
        # TODO: pass uv to a vec2 output fragUV
        vs_source = dedent("""
            #version 330
            uniform mat4 projection;
            in vec3 position;
            in vec3 color;
            out vec3 fragColor;
            void main()
            {
               gl_Position = projection * vec4(position, 1.0);
               fragColor = color;
            }\
        """)
        vs = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vs, vs_source)
        glCompileShader(vs)
        glAttachShader(program, vs)
        if glGetShaderiv(vs, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(vs))

        # fragment shader
        # TODO: add a vec2 input fragUV
        # TODO: add a uniform sampler2D variable for the texture
        fs_source = dedent("""
            #version 330
            in vec3 fragColor;
            out vec4 color_out;
            void main()
            {
               color_out = vec4(fragColor, 1.0);
            }\
        """)
        fs = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fs, fs_source)
        glCompileShader(fs)
        glAttachShader(program, fs)
        if glGetShaderiv(fs, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(fs))

        # use the program
        glLinkProgram(program)
        glUseProgram(program)

        return program


    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.renderCube()


    def renderCube(self):
        glUseProgram(self.cubeProgram)
        glBindVertexArray(self.cubeVao)
        glDrawElements(
            GL_TRIANGLE_FAN,
            len(self.indices),
            GL_UNSIGNED_INT,
            c_void_p(0)
        )


    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

        camera = QMatrix4x4()
        camera.perspective(60, 4.0/3.0, 0.01, 100)
        camera.lookAt(QVector3D(2, 2, 2), QVector3D(0, 0, 0), QVector3D(0, 0, 1))

        glUseProgram(self.cubeProgram)
        glUniformMatrix4fv(
            self.cubeProjection,
            1,
            GL_FALSE,
            array('f', camera.data()).tostring()
        )


    def sizeof(self, a):
        return a.itemsize * len(a)


if __name__ == '__main__':

    width = 640
    height = 480

    app = QApplication(sys.argv)
    w = Texture()
    w.show()

    sys.exit(app.exec_())
