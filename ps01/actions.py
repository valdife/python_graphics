import json
from tkinter import Canvas, filedialog
from models import Line, Rectangle, Point, Circle, Shape


SHAPES={
    'line': Line,
    'rectangle': Rectangle,
    'circle': Circle,
}


def clear_canvas(canvas: Canvas):
    canvas.delete('all')

def draw_from_input(canvas: Canvas, shape: str, point1_x: str, point1_y: str, point2_x: str, point2_y: str, radius: str, serializer_list: list[Shape]):
    try:
        shape = SHAPES[shape.lower()]
    except KeyError:
        raise ValueError("Cannot reach selected shape in SHAPES dictionary")

    point1 = Point(int(point1_x), int(point1_y))
    point2 = Point(int(point2_x), int(point2_y))
    radius = int(radius)

    if shape != Circle:
        shape_object = shape(point1=point1, point2=point2)
        shape_object.draw(canvas)
        serializer_list.append(shape_object.serialize())
    else:
        shape_object = shape(point=point1, radius=radius)
        shape_object.draw(canvas)
        serializer_list.append(shape_object.serialize())

def file_save(serializer_list: list[dict]):
    f = filedialog.asksaveasfile(mode='w', defaultextension=".json")
    if f is None:
        return
    f.write(json.dumps(serializer_list))
    f.close()

def load_from_file(canvas: Canvas):
    f = filedialog.askopenfile(mode='r', defaultextension=".json")
    if f is None:
        return
    json_data = json.loads(f.read())
    f.close()

    for shape in json_data:
        deserialize_from_dict(canvas=canvas, object_data=shape)

def deserialize_from_dict(canvas: Canvas, object_data: dict) -> None:
    try:
        shape = object_data['type']
        shape_object = SHAPES[shape.lower()]
        if shape_object == Circle:
            point = Point(object_data['points'][0]['x'], object_data['points'][0]['y'])
            radius = object_data['radius']
            shape_object = shape_object(point=point, radius=radius)
        else:
            shape_object = shape_object(Point(0, 0), Point(0, 0))
        shape_object.deserialize(json_data=object_data, canvas=canvas)
    except KeyError:
        raise ValueError("Invalid JSON data")
