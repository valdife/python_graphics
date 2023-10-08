import json, math
from random import randint
from tkinter import Canvas


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def distance_to(self, other_point):
        return math.sqrt((self.x - other_point.x)**2 + (self.y - other_point.y)**2)

class Shape:
    def __init__(self, shape: str, point1: Point, point2: Point):
        self.points = [point1, point2]
        self.shape = None
        self.id = None

    def draw(self): ...

    def update(self): ...

    def serialize(self, points: list[Point]) -> dict:
        return {
            'type': self.shape,
            'points': [
                {
                    'x': point.x,
                    'y': point.y
                } for point in points
            ]
        }

    def deserialize(self, json_data: dict) -> None:
        try:
            self.shape = json_data['type']
            self.points = [Point(point['x'], point['y']) for point in json_data['points']]
        except KeyError:
            raise ValueError("Invalid JSON data")

    def is_point_part_of_shape(self, point: Point) -> bool: ...

class Line(Shape):
    def __init__(self, point1: Point, point2: Point):
        super().__init__('line', point1, point2)

    def draw(self, canvas: Canvas) -> None:
        self.id = canvas.create_line(self.points[0].x, self.points[0].y, self.points[1].x, self.points[1].y)

    def update(self, canvas: Canvas) -> None:
        canvas.coords(self.id, self.points[0].x, self.points[0].y, self.points[1].x, self.points[1].y)

    def is_point_part_of_shape(self, point: Point) -> bool:
        return self.points[0].distance_to(point) + self.points[1].distance_to(point) == self.points[0].distance_to(self.points[1])

class Circle(Shape):
    def __init__(self, point: Point, radius: int):
        point1 = Point(point.x - radius, point.y - radius)
        point2 = Point(point.x + radius, point.y + radius)
        super().__init__('circle', point1, point2)
        self.radius = radius

    def draw(self, canvas: Canvas) -> None:
        self.id = canvas.create_oval(self.points[0].x, self.points[0].y, self.points[1].x, self.points[1].y)

    def update(self, canvas: Canvas, point: Point) -> None:
        point1 = Point(point.x - self.radius, point.y - self.radius)
        point2 = Point(point.x + self.radius, point.y + self.radius)
        self.points = [point1, point2]
        canvas.coords(self.id, self.points[0].x, self.points[0].y, self.points[1].x, self.points[1].y)

    def is_point_part_of_shape(self, point: Point) -> bool:
        return self.points[0].distance_to(point) <= self.radius

class Rectangle(Shape):
    def __init__(self, point1: Point, point2: Point):
        super().__init__('rectangle', point1, point2)

    def draw(self, canvas: Canvas) -> None:
        self.id = canvas.create_rectangle(self.points[0].x, self.points[0].y, self.points[1].x, self.points[1].y)

    def update(self, canvas: Canvas) -> None:
        canvas.coords(self.id, self.points[0].x, self.points[0].y, self.points[1].x, self.points[1].y)

    def is_point_part_of_shape(self, point: Point) -> bool:
        return self.points[0].x <= point.x <= self.points[1].x and self.points[0].y <= point.y <= self.points[1].y
