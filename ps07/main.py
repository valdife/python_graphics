import tkinter as tk
import math
import json

points = []
polygon_objects = []
pivot_point = None
selected_polygon = None
polygon_coords = None


def clear_canvas():
    canvas.delete("all")
    points.clear()
    for poly in polygon_objects:
        canvas.delete(poly)
    global pivot_point
    if pivot_point:
        canvas.delete(pivot_point)
        pivot_point = None
    info_label.config(text="")


def exit_app():
    root.destroy()


def on_left_click(event):
    global pivot_point
    if mode.get() == "Drawing":
        canvas.delete("PivotMoved")
        canvas.delete("PivotMovedLine")
        points.append((event.x, event.y))
        canvas.create_oval(
            event.x, event.y, event.x + 5, event.y + 5, fill="black", tags="Vertex"
        )  # Draw a point
    if mode.get() == "Selecting":
        canvas.delete("PivotMoved")
        canvas.delete("PivotMovedLine")
        get_polygon(event)
    elif mode.get() == "Point":
        canvas.delete("PivotMoved")
        canvas.delete("PivotMovedLine")
        canvas.delete("Pivot")
        pivot_point = (event.x, event.y)
        canvas.create_oval(
            event.x - 2.5,
            event.y - 2.5,
            event.x + 2.5,
            event.y + 2.5,
            fill="red",
            outline="red",
            tags="Pivot",
        )
    elif (
        mode.get() == "VectorMove"
        or mode.get() == "VectorRotate"
        or mode.get() == "VectorScale"
    ):
        enable_vector_move()


def on_right_click(event):
    if mode.get() == "Drawing":
        if points:
            print(points)
            canvas.create_polygon(
                points, outline="black", fill="white"
            )  # Draw a polygon
            polygon_objects.append(canvas.find_all()[-1])
            points.clear()


def get_polygon(event):
    x, y = event.x, event.y
    global selected_polygon, polygon_coords
    for poly in polygon_objects:
        items = canvas.find_overlapping(x, y, x, y)
        if poly in items:
            selected_polygon = poly
            canvas.drag_data = {"item": selected_polygon, "x": x, "y": y}
            draw_selected_polygon_vertices(poly)

            polygon_coords = canvas.coords(selected_polygon)


def draw_selected_polygon_vertices(polygon):
    polygon_coords = canvas.coords(polygon)
    canvas.delete("Vertex")
    for i in range(0, len(polygon_coords), 2):
        x_coord, y_coord = polygon_coords[i], polygon_coords[i + 1]
        canvas.create_oval(
            x_coord - 2,
            y_coord - 2,
            x_coord + 2,
            y_coord + 2,
            fill="blue",
            outline="blue",
            tags="Vertex",
        )


def enable_vector_move():
    global pivot_point, selected_polygon
    if pivot_point and selected_polygon:
        info_label.config(text="Vector enabled")
    elif pivot_point and not selected_polygon:
        mode.set("Selecting")
        info_label.config(text="Select a polygon first")
    elif not pivot_point and selected_polygon:
        mode.set("Point")
        info_label.config(text="Create a pivot point first")
    elif not pivot_point and not selected_polygon:
        mode.set("Selecting")
        info_label.config(text="Select a polygon first")


def on_left_mouse_drag(event):
    global selected_polygon, pivot_point, polygon_coords
    if mode.get() == "Moving" and hasattr(canvas, "drag_data"):
        x, y = event.x, event.y
        delta_x = x - canvas.drag_data["x"]
        delta_y = y - canvas.drag_data["y"]
        canvas.move(canvas.drag_data["item"], delta_x, delta_y)
        canvas.drag_data["x"] = x
        canvas.drag_data["y"] = y

        # Move all the vertex ovals together with the polygon
        if selected_polygon:
            vertex_ovals = canvas.find_withtag("Vertex")
            for oval in vertex_ovals:
                canvas.move(oval, delta_x, delta_y)
    if mode.get() == "VectorMove":
        x, y = event.x, event.y
        dx = x - pivot_point[0]
        dy = y - pivot_point[1]
        new_points = vector_move(polygon_coords, dx, dy)

        # Clear previous drawings
        canvas.delete("PivotMoved")
        canvas.delete("PivotMovedLine")

        # Draw the moved vector
        for i in range(0, len(new_points), 2):
            x_coord, y_coord = new_points[i], new_points[i + 1]
            canvas.create_oval(
                x_coord + 4,
                y_coord - 4,
                x_coord - 4,
                y_coord - 4,
                fill="blue",
                outline="blue",
                tags="PivotMoved",
            )
            canvas.create_line(
                pivot_point[0],
                pivot_point[1],
                x_coord,
                y_coord,
                width=1,
                fill="blue",
                tags="PivotMovedLine",
            )
            canvas.create_line(
                pivot_point[0],
                pivot_point[1],
                x,
                y,
                width=1,
                fill="green",
                tags="PivotMovedLine",
            )

        canvas.delete(selected_polygon)
        canvas.create_polygon(new_points, outline="black", fill="white")
        polygon_objects.append(canvas.find_all()[-1])
        selected_polygon = canvas.find_all()[-1]

    elif mode.get() == "VectorRotate":
        x, y = event.x, event.y
        angle = calculate_rotation_angle(pivot_point, (x, y))
        new_points = vector_rotate(polygon_coords, angle)

        # Clear previous drawings
        canvas.delete("PivotMoved")
        canvas.delete("PivotMovedLine")

        # Draw the rotated vector
        for i in range(0, len(new_points), 2):
            x_coord, y_coord = new_points[i], new_points[i + 1]
            canvas.create_oval(
                x_coord + 4,
                y_coord - 4,
                x_coord - 4,
                y_coord - 4,
                fill="blue",
                outline="blue",
                tags="PivotMoved",
            )
            canvas.create_line(
                pivot_point[0],
                pivot_point[1],
                x_coord,
                y_coord,
                width=1,
                fill="blue",
                tags="PivotMovedLine",
            )
            canvas.create_line(
                pivot_point[0],
                pivot_point[1],
                x,
                y,
                width=1,
                fill="green",
                tags="PivotMovedLine",
            )

        canvas.delete(selected_polygon)
        canvas.create_polygon(new_points, outline="black", fill="white")
        polygon_objects.append(canvas.find_all()[-1])
        selected_polygon = canvas.find_all()[-1]
    elif mode.get() == "VectorScale":
        x, y = event.x, event.y
        scale_factor = calculate_scale_factor(pivot_point, (x, y))
        new_points = vector_scale(polygon_coords, scale_factor)

        # Clear previous drawings
        canvas.delete("PivotMoved")
        canvas.delete("PivotMovedLine")

        # Draw the scaled vector
        for i in range(0, len(new_points), 2):
            x_coord, y_coord = new_points[i], new_points[i + 1]
            canvas.create_oval(
                x_coord + 4,
                y_coord - 4,
                x_coord - 4,
                y_coord - 4,
                fill="blue",
                outline="blue",
                tags="PivotMoved",
            )
            canvas.create_line(
                pivot_point[0],
                pivot_point[1],
                x_coord,
                y_coord,
                width=1,
                fill="blue",
                tags="PivotMovedLine",
            )
            canvas.create_line(
                pivot_point[0],
                pivot_point[1],
                x,
                y,
                width=1,
                fill="green",
                tags="PivotMovedLine",
            )

        canvas.delete(selected_polygon)
        canvas.create_polygon(new_points, outline="black", fill="white")
        polygon_objects.append(canvas.find_all()[-1])
        selected_polygon = canvas.find_all()[-1]


def vector_move(polygon_coords, dx, dy):
    new_points = []

    for i in range(0, len(polygon_coords), 2):
        x_coord, y_coord = polygon_coords[i], polygon_coords[i + 1]
        new_x = x_coord + dx
        new_y = y_coord + dy
        new_points.append(new_x)
        new_points.append(new_y)

    return new_points


def vector_rotate(polygon_coords, angle):
    global pivot_point
    new_points = []
    pivot_x = pivot_point[0]
    pivot_y = pivot_point[1]
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)

    for i in range(0, len(polygon_coords), 2):
        x_coord, y_coord = polygon_coords[i], polygon_coords[i + 1]
        new_x = (
            pivot_x + (x_coord - pivot_x) * cos_angle - (y_coord - pivot_y) * sin_angle
        )
        new_y = (
            pivot_y + (x_coord - pivot_x) * sin_angle + (y_coord - pivot_y) * cos_angle
        )
        new_points.append(new_x)
        new_points.append(new_y)

    return new_points


def calculate_rotation_angle(pivot_point, current_position):
    pivot_x, pivot_y = pivot_point
    x, y = current_position
    angle = math.atan2(y - pivot_y, x - pivot_x)
    return angle


def calculate_scale_factor(pivot_point, current_position):
    pivot_x, pivot_y = pivot_point
    x, y = current_position
    scale_factor = (
        math.sqrt((x - pivot_x) ** 2 + (y - pivot_y) ** 2) / 100
    )  # Adjust the denominator as needed
    return scale_factor


def vector_scale(polygon_coords, scale_factor):
    global pivot_point
    new_points = []
    pivot_x = pivot_point[0]
    pivot_y = pivot_point[1]

    for i in range(0, len(polygon_coords), 2):
        x_coord, y_coord = polygon_coords[i], polygon_coords[i + 1]
        new_x = pivot_x + (x_coord - pivot_x) * scale_factor
        new_y = pivot_y + (y_coord - pivot_y) * scale_factor
        new_points.append(new_x)
        new_points.append(new_y)

    return new_points


def on_stop_drag(event):
    if mode.get() == "123":
        canvas.delete("PivotMoved")
        canvas.delete("PivotMovedLine")


def apply_vector_operation(operation, parameter):
    if selected_polygon:
        if operation == "VectorMove":
            new_points = vector_move(polygon_coords, parameter)
            perform_operations(new_points)
        elif operation == "VectorRotate":
            angle = math.radians(parameter)
            new_points = vector_rotate(polygon_coords, angle)
            perform_operations(new_points)
        elif operation == "VectorScale":
            new_points = vector_scale(polygon_coords, parameter)
            perform_operations(new_points)
    else:
        info_label.config(text="Select a polygon first")


def perform_operations(new_points):
    global selected_polygon
    canvas.delete(selected_polygon)
    canvas.create_polygon(new_points, outline="black", fill="white")
    polygon_objects.append(canvas.find_all()[-1])
    selected_polygon = canvas.find_all()[-1]


# Function to apply VectorMove
def apply_vector_move():
    try:
        dx = float(vector_move_entry_x.get())
        dy = float(vector_move_entry_y.get())
        apply_vector_operation("VectorMove", (dx, dy))
    except ValueError:
        info_label.config(text="Invalid input for Vector Move")


# Function to apply VectorRotate
def apply_vector_rotate():
    try:
        angle_degrees = float(vector_rotate_entry.get())
        apply_vector_operation("VectorRotate", angle_degrees)
    except ValueError:
        info_label.config(text="Invalid input for Rotation Angle")


# Function to apply VectorScale
def apply_vector_scale():
    try:
        scale_factor = float(vector_scale_entry.get())
        apply_vector_operation("VectorScale", scale_factor)
    except ValueError:
        info_label.config(text="Invalid input for Scale Factor")


def save_to_json():
    non_empty_polygons = [
        canvas.coords(polygon) for polygon in polygon_objects if canvas.coords(polygon)
    ]
    data = {
        "polygons": non_empty_polygons,
        "pivot_point": pivot_point,
    }

    with open("saved_data.json", "w") as json_file:
        json.dump(data, json_file)


def load_from_json():
    try:
        with open("saved_data.json", "r") as json_file:
            data = json.load(json_file)
            if "polygons" in data and "pivot_point" in data:
                clear_canvas()
                for polygon_coords in data["polygons"]:
                    if len(polygon_coords) > 0:
                        canvas.create_polygon(
                            polygon_coords, outline="black", fill="white"
                        )
                        polygon_objects.append(canvas.find_all()[-1])
                pivot_point = data["pivot_point"]

                canvas.create_oval(
                    pivot_point[0] - 4,
                    pivot_point[1] - 4,
                    pivot_point[0] + 4,
                    pivot_point[1] + 4,
                    fill="red",
                    outline="red",
                    tags="Point",
                )
    except FileNotFoundError:
        info_label.config(text="No saved data found")


root = tk.Tk()
root.title("Draw and Edit Polygons")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}+0+0")

menu_frame = tk.Frame(root, bg="lightgray")
menu_frame.pack(side="left", fill="y")

clear_button = tk.Button(menu_frame, text="Clear Canvas", command=clear_canvas)
exit_button = tk.Button(menu_frame, text="Exit", command=exit_app)
clear_button.pack(pady=2)
exit_button.pack(pady=2)

mode = tk.StringVar()
mode.set("Drawing")

draw_button = tk.Radiobutton(
    menu_frame, text="Draw Polygon", variable=mode, value="Drawing"
)
select_polygon = tk.Radiobutton(
    menu_frame, text="Select Polygon", variable=mode, value="Selecting"
)
create_point_button = tk.Radiobutton(
    menu_frame, text="Create Point", variable=mode, value="Point"
)
edit_button = tk.Radiobutton(
    menu_frame, text="Move Polygon", variable=mode, value="Moving"
)
vector_move_button = tk.Radiobutton(
    menu_frame, text="Vector Move", variable=mode, value="VectorMove"
)

vector_rota_button = tk.Radiobutton(
    menu_frame, text="Vector Rotate", variable=mode, value="VectorRotate"
)

vector_sc_button = tk.Radiobutton(
    menu_frame, text="Vector Scale", variable=mode, value="VectorScale"
)
draw_button.pack(pady=2)
select_polygon.pack(pady=2)
edit_button.pack(pady=2)
create_point_button.pack(pady=2)
vector_move_button.pack(pady=2)

vector_rota_button.pack(pady=2)
vector_sc_button.pack(pady=2)

vector_move_label = tk.Label(menu_frame, text="Vector Move (dx, dy):")
vector_move_entry_x = tk.Entry(menu_frame, width=10)
vector_move_entry_y = tk.Entry(menu_frame, width=10)
vector_move_button = tk.Button(menu_frame, text="Apply Vector Move")

vector_rotate_label = tk.Label(menu_frame, text="Rotation Angle (degrees):")
vector_rotate_entry = tk.Entry(menu_frame, width=10)
vector_rotate_button = tk.Button(menu_frame, text="Apply Rotation")

vector_scale_label = tk.Label(menu_frame, text="Scale Factor:")
vector_scale_entry = tk.Entry(menu_frame, width=10)
vector_scale_button = tk.Button(menu_frame, text="Apply Scaling")

vector_move_label.pack(pady=2)
vector_move_entry_x.pack(pady=5)
vector_move_entry_y.pack(pady=5)
vector_move_button.pack(pady=2)

vector_rotate_label.pack(pady=2)
vector_rotate_entry.pack(pady=5)
vector_rotate_button.pack(pady=2)

vector_scale_label.pack(pady=2)
vector_scale_entry.pack(pady=5)
vector_scale_button.pack(pady=2)

vector_move_button.config(command=apply_vector_move)
vector_rotate_button.config(command=apply_vector_rotate)
vector_scale_button.config(command=apply_vector_scale)


save_button = tk.Button(menu_frame, text="Save to JSON", command=save_to_json)
load_button = tk.Button(menu_frame, text="Load from JSON", command=load_from_json)

save_button.pack(pady=2)
load_button.pack(pady=2)
info_label = tk.Label(menu_frame, text="")
info_label.pack()

canvas = tk.Canvas(root, bg="white")
canvas.pack(side="right", fill="both", expand=True)

canvas.bind("<Button-1>", on_left_click)  # Left-click for Drawing or Editing
canvas.bind("<Button-3>", on_right_click)  # Right-click for Drawing
canvas.bind("<B1-Motion>", on_left_mouse_drag)  # Drag polygons in Editing mode

canvas.bind("<ButtonRelease-1>", on_stop_drag)
root.mainloop()
