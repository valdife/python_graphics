import numpy as np
import pygame
import pygame as pg
import pyrr
from PIL import Image
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import compileShader, compileProgram
from pygame.constants import *
import matplotlib.pyplot as plt


def display_image_with_matplotlib(image):
    plt.imshow(image)
    plt.axis('off')  # Hide axis
    plt.show()

def create_color_image(intersection_point):
    normalized_point = (intersection_point + 0.5) / 1.0
    # Create a new image with RGB mode and dimensions 256x256 pixels
    image = Image.new("RGB", (256, 256))

    # Extract the Red value from the intersection point
    red_value = int(normalized_point[0] * 255)

    # Create an image with the specified Red value for all pixels
    data = [(red_value, g, b) for g in range(256) for b in range(256)]

    # Set the pixel data for the image
    image.putdata(data)

    # Display the image using Matplotlib GUI
    display_image_with_matplotlib(image)

class App:

    def __init__(self):
        pg.init()
        pg.display.set_mode((640, 480), pg.OPENGL | pg.DOUBLEBUF)
        self.clock = pg.time.Clock()

        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)
        self.shader = self.create_shader('vertex.txt', 'fragment.txt')
        glUseProgram(self.shader)
        
        self.cube_mesh = CubeMesh()
        self.cube = Cube(
            position=[0, 0, -3],
            eulers=[10, 10, 10]
        )

        # create perspective
        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy=45, aspect=640 / 480,
            near=0.1, far=10, dtype=np.float32
        )
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "projection"),
                           1, GL_FALSE, projection_transform)

        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        self.mainLoop()

    def create_shader(self, vertex_file_path, fragment_vertex_path):
        with open(vertex_file_path, 'r') as file:
            vertex_src = file.readlines()

        with open(fragment_vertex_path, 'r') as file:
            fragment_src = file.readlines()

        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER),
        )
        return shader

    def mainLoop(self):
        running = True
        right_mouse_button_pressed = False
        prev_mouse_pos = (0, 0)

        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:  # Right mouse button
                    right_mouse_button_pressed = True
                    prev_mouse_pos = pg.mouse.get_pos()
                elif event.type == pg.MOUSEBUTTONUP and event.button == 3:  # Right mouse button
                    right_mouse_button_pressed = False
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                    if not right_mouse_button_pressed:
                        click_x, click_y = pg.mouse.get_pos()
                        self.check_cube_intersection(click_x, click_y)

            if right_mouse_button_pressed:
                current_mouse_pos = pg.mouse.get_pos()
                mouse_dx, mouse_dy = current_mouse_pos[0] - prev_mouse_pos[0], current_mouse_pos[1] - prev_mouse_pos[1]
                prev_mouse_pos = current_mouse_pos

                self.cube.eulers[0] += mouse_dy * 0.5
                self.cube.eulers[1] += mouse_dx * 0.5

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glUseProgram(self.shader)

            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform,
                m2=pyrr.matrix44.create_from_eulers(
                    eulers=np.radians(self.cube.eulers), dtype=np.float32
                )
            )
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform,
                m2=pyrr.matrix44.create_from_translation(
                    vec=np.array(self.cube.position), dtype=np.float32
                )
            )
            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, model_transform)

            glBindVertexArray(self.cube_mesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)

            pg.display.flip()

            self.clock.tick(60)

        self.quit()

    def check_cube_intersection(self, click_x, click_y):
        model_view = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)

        win_x, win_y, win_z = gluUnProject(click_x, click_y, 0, model_view, projection, viewport)
        ray_start = np.array([win_x, win_y, win_z], dtype=np.float64)

        win_x, win_y, win_z = gluUnProject(click_x, click_y, 1, model_view, projection, viewport)
        ray_end = np.array([win_x, win_y, win_z], dtype=np.float64)

        intersection_point = self.cube_mesh.intersect_ray_with_cube(ray_start, ray_end)
        if intersection_point is not None:
            print(f"Intersection Point: {self.map_point_to_color(intersection_point)}")
            create_color_image(intersection_point)

    def map_point_to_color(self, point):
        # Normalize the point coordinates to the range [0, 1]
        normalized_point = (point + 0.5) / 1.0  # Assuming the cube's side length is 1

        # Map the normalized coordinates to the RGB color channels
        r = int(normalized_point[0] * 255)
        g = int(normalized_point[1] * 255)
        b = int(normalized_point[2] * 255)

        return r, g, b

    def quit(self):
        self.cube_mesh.destroy()
        glDeleteProgram(self.shader)

        pg.quit()


class CubeMesh:
    def __init__(self):
        self.verticies = (
            -0.5, -0.5, -0.5, 0, 1, 0,  # green
            0.5, -0.5, -0.5, 0, 1, 1,  # green blue
            0.5, 0.5, -0.5, 1, 1, 1,  # white

            0.5, 0.5, -0.5, 1, 1, 1,  # white   
            -0.5, 0.5, -0.5, 1, 1, 0,  # green red
            -0.5, -0.5, -0.5, 0, 1, 0,  # green

            -0.5, -0.5, 0.5, 0, 0, 0,  # black
            0.5, -0.5, 0.5, 0, 0, 1,  # blue
            0.5, 0.5, 0.5, 1, 0, 1,  # red Blue

            0.5, 0.5, 0.5, 1, 0, 1,  # red Blue
            -0.5, 0.5, 0.5, 1, 0, 0,  # red
            -0.5, -0.5, 0.5, 0, 0, 0,  # black

            -0.5, 0.5, 0.5, 1, 0, 0,  # red
            -0.5, 0.5, -0.5, 1, 1, 0,  # green red
            -0.5, -0.5, -0.5, 0, 1, 0,  # green

            -0.5, -0.5, -0.5, 0, 1, 0,  # green
            -0.5, -0.5, 0.5, 0, 0, 0,  # white
            -0.5, 0.5, 0.5, 1, 0, 0,  # red

            0.5, 0.5, 0.5, 1, 0, 1,  # red blue
            0.5, 0.5, -0.5, 1, 1, 1,  # white
            0.5, -0.5, -0.5, 0, 1, 1,  # green blue

            0.5, -0.5, -0.5, 0, 1, 1,  # green blue
            0.5, -0.5, 0.5, 0, 0, 1,  # blue
            0.5, 0.5, 0.5, 1, 0, 1,  # red blue

            -0.5, -0.5, -0.5, 0, 1, 0,  # green
            0.5, -0.5, -0.5, 0, 1, 1,  # green blue
            0.5, -0.5, 0.5, 0, 0, 1,  # blue

            0.5, -0.5, 0.5, 0, 0, 1,  # blue
            -0.5, -0.5, 0.5, 0, 0, 0,  # black
            -0.5, -0.5, -0.5, 0, 1, 0,  # green

            -0.5, 0.5, -0.5, 1, 1, 0,  # green red
            0.5, 0.5, -0.5, 1, 1, 1,  # white
            0.5, 0.5, 0.5, 1, 0, 1,  # red blue

            0.5, 0.5, 0.5, 1, 0, 1,  # red blue
            -0.5, 0.5, 0.5, 1, 0, 0,  # red
            -0.5, 0.5, -0.5, 1, 1, 0,  # green red
        )

        self.verticies = np.array(self.verticies, dtype=np.float32)

        self.vertex_count = len(self.verticies) // 6  # Number of vertices

        # Create a Vertex Array Object (VAO) and Vertex Buffer Object (VBO)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.verticies.nbytes, self.verticies, GL_STATIC_DRAW)

        # Define vertex attribute pointers
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def get_faces(self):
        # Split the vertices into individual faces
        faces = []
        for i in range(0, len(self.verticies), 18):
            vertices = self.verticies[i:i + 18]
            faces.append(vertices)
        return faces
    
    # Method to calculate the intersection of a ray with a face
    def intersect_ray_with_face(self, ray_start, ray_end, face):
        # Extract face vertices
        vertices = np.array(face, dtype=np.float64).reshape(6, 3)
        epsilon = 1e-6  # A small value to avoid division by zero

        # Calculate the normal of the face
        normal = np.cross(vertices[1] - vertices[0], vertices[2] - vertices[0])
        normal /= np.linalg.norm(normal)

        # Calculate the plane equation of the face: Ax + By + Cz + D = 0
        A, B, C = normal
        D = -np.dot(normal, vertices[0])

        # Calculate the direction vector of the ray
        direction = ray_end - ray_start
        direction /= np.maximum(np.linalg.norm(direction), epsilon)  # Normalize the direction vector

        # Calculate the denominator for the ray-plane intersection
        denominator = np.dot(normal, direction)

        # Check if the ray and the plane are parallel (no intersection)
        if abs(denominator) < epsilon:
            return None

        # Calculate the distance from the ray start to the intersection point
        t = -(np.dot(normal, ray_start) + D) / denominator

        # Check if the intersection point is behind the ray start
        if t < 0:
            return None

        # Calculate the intersection point in 3D space
        intersection_point = ray_start + t * direction

        # Check if the intersection point is inside the bounds of the face
        for i in range(3):
            if intersection_point[i] < min(vertices[:, i]) - epsilon or intersection_point[i] > max(vertices[:, i]) + epsilon:
                return None

        return intersection_point

    # Method to calculate ray-cube intersections
    def intersect_ray_with_cube(self, ray_start, ray_end):
        faces = self.get_faces()
        for face in faces:
            intersection_point = self.intersect_ray_with_face(ray_start, ray_end, face)
            if intersection_point is not None:
                return intersection_point
        return None

    def destroy(self):
        glDeleteBuffers(1, (self.vbo,))
        glDeleteVertexArrays(1, (self.vao,))

# Class to represent a cube
class Cube:
    def __init__(self, position, eulers):
        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

if __name__ == '__main__':
    myApp = App()