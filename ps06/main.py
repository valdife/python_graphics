import tkinter as tk
import numpy as np


def start_mouse_draw():
    global drawing, points, anchor_points, editing
    drawing = True
    editing = False
    points = []
    anchor_points = []
    edited_point = None
    clear_canvas()


def draw_bezier_curve():
    clear_canvas()

    canvas.delete("curve")
    canvas.delete("edit_points")

    if random_curve_displayed:
        anchor_points = points
    else:
        anchor_points = []
        for i in range(degree):
            x = np.random.randint(10, 1450)
            y = np.random.randint(10, 850)
            anchor_points.append((x, y))

    for i in range(len(anchor_points) - 1):
        canvas.create_line(
            anchor_points[i], anchor_points[i + 1], fill="blue", tags="curve_line"
        )

    step = 0.01
    t = 0
    while t <= 1:
        x, y = bezier_interpolation(anchor_points, t)
        canvas.create_oval(x, y, x, y, width=2, fill="red", tags="curve")
        t += step

    for point in anchor_points:
        canvas.create_oval(
            point[0],
            point[1],
            point[0],
            point[1],
            width=2,
            fill="blue",
            tags="edit_points",
        )


def clear_canvas():
    canvas.delete("curve")
    canvas.delete("edit_points")
    canvas.delete("anchor")
    canvas.delete("curve_line")


def draw_curve(event):
    global drawing, editing
    if editing:
        return
    drawing = False
    degree = len(anchor_points) - 1
    if degree >= 1:
        step = 0.005
        t = 0
        while t <= 1:
            x, y = bezier_interpolation(anchor_points, t)
            canvas.create_oval(x, y, x, y, width=1, fill="red", tags="curve")
            t += step
    for i in range(len(anchor_points) - 1):
        canvas.create_line(
            anchor_points[i], anchor_points[i + 1], fill="blue", tags="curve_line"
        )


def bezier_interpolation(points, t):
    n = len(points) - 1
    x, y = 0, 0
    for i in range(n + 1):
        b = binomial_coefficient(n, i)
        x += b * ((1 - t) ** (n - i)) * (t**i) * points[i][0]
        y += b * ((1 - t) ** (n - i)) * (t**i) * points[i][1]
    return x, y


def binomial_coefficient(n, k):
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    return binomial_coefficient(n - 1, k - 1) + binomial_coefficient(n - 1, k)


def update_coordinates_text(x, y):
    x_coord.set(x)
    y_coord.set(y)


def canvas_click(event):
    global drawing, editing, edited_point
    if drawing:
        x, y = event.x, event.y
        points.append((x, y))
        anchor_points.append((x, y))
        edited_point = None
        canvas.create_oval(
            x, y, x, y, width=5, fill="blue", outline="red", tags="anchor"
        )
        update_coordinates_text(x, y)
    elif editing:
        x, y = event.x, event.y
        closest_point = find_closest_control_point(x, y)
        if closest_point is not None:
            edited_point = closest_point
            update_curve()


def edit_curve():
    global editing
    editing = True


def update_curve():
    global anchor_points
    clear_canvas()
    degree = len(points) - 1
    if degree >= 1:
        step = 0.005
        t = 0
        while t <= 1:
            x, y = bezier_interpolation(points, t)
            canvas.create_oval(x, y, x, y, width=1, fill="red", tags="curve")
            t += step
    for i in range(len(points) - 1):
        canvas.create_line(points[i], points[i + 1], fill="blue", tags="curve_line")


def find_closest_control_point(x, y):
    for i, (px, py) in enumerate(points):
        if (x - px) ** 2 + (y - py) ** 2 <= 25:
            return i
    return None


random_curve_displayed = False


def generate_random_curve():
    global degree, random_curve_displayed, points, anchor_points
    try:
        if random_curve_displayed:
            clear_canvas()
            random_curve_displayed = False

        degree = int(degree_entry.get())
        points = []
        anchor_points = []

        for i in range(degree):
            x = np.random.randint(10, 1350)
            y = np.random.randint(10, 750)
            points.append((x, y))
            anchor_points.append((x, y))

        for i in range(len(points) - 1):
            canvas.create_line(points[i], points[i + 1], fill="blue", tags="curve_line")

        random_curve_displayed = True
        update_curve()

        for point in points:
            canvas.create_oval(
                point[0],
                point[1],
                point[0],
                point[1],
                width=5,
                fill="blue",
                outline="red",
                tags="anchor",
            )

    except ValueError:
        pass


def drag_control_point(event):
    global editing, edited_point, drag_data_x, drag_data_y, anchor_points

    if editing and edited_point is not None:
        x, y = event.x, event.y

        if drag_data_x is None:
            drag_data_x = x - points[edited_point][0]
            drag_data_y = y - points[edited_point][1]

        new_x = x - drag_data_x
        new_y = y - drag_data_y

        points[edited_point] = (new_x, new_y)
        update_curve()

        canvas.delete("edit_points")
        canvas.delete("anchor")
        canvas.delete("curve_line")

        update_coordinates_text(x, y)
        for point in points:
            canvas.create_oval(
                point[0],
                point[1],
                point[0],
                point[1],
                width=5,
                fill="blue",
                outline="red",
                tags="edit_points",
            )
        for i in range(len(points) - 1):
            canvas.create_line(points[i], points[i + 1], fill="blue", tags="curve_line")


def save_coordinates():
    global edited_point, points
    if edited_point is not None:
        x = int(x_coord.get())
        y = int(y_coord.get())
        points[edited_point] = (x, y)
        update_curve()
        canvas.delete("edit_points")
        canvas.delete("anchor")

        update_coordinates_text(x, y)
        for point in points:
            canvas.create_oval(
                point[0],
                point[1],
                point[0],
                point[1],
                width=5,
                fill="blue",
                outline="red",
                tags="edit_points",
            )


root = tk.Tk()
root.title("Krzywa Béziera")
root.geometry("1920x1080")

menu_frame = tk.Frame(root)
menu_frame.pack(side=tk.LEFT)

canvas_frame = tk.Frame(root)
canvas_frame.pack(side=tk.LEFT)

draw_button = tk.Button(
    menu_frame, text="Rysuj krzywą myszką", command=start_mouse_draw
)
draw_button.pack()

clear_button = tk.Button(menu_frame, text="Wyczyść canvas", command=clear_canvas)
clear_button.pack()

edit_button = tk.Button(menu_frame, text="Edit Curve", command=edit_curve)
edit_button.pack()

x_coord = tk.StringVar()
y_coord = tk.StringVar()

x_label = tk.Label(menu_frame, text="X:")
x_label.pack()
x_entry = tk.Entry(menu_frame, textvariable=x_coord, width=10)
x_entry.pack()
y_label = tk.Label(menu_frame, text="Y:")
y_label.pack()

y_entry = tk.Entry(menu_frame, textvariable=y_coord, width=10)
y_entry.pack()

save_button = tk.Button(menu_frame, text="Save", command=save_coordinates)
save_button.pack()

degree_label = tk.Label(menu_frame, text="Degree:")
degree_label.pack()
degree_entry = tk.Entry(menu_frame, width=10)
degree_entry.pack()
degree_entry.insert(0, 3)

generate_curve_button = tk.Button(
    menu_frame, text="Generate Curve", command=generate_random_curve
)
generate_curve_button.pack()

canvas = tk.Canvas(canvas_frame, width=1920, height=1080)
canvas.pack()

canvas.bind("<Button-1>", canvas_click)
canvas.bind("<Button-3>", draw_curve)
canvas.bind("<B1-Motion>", drag_control_point)

drawing = False
editing = False
edited_point = None
points = []
anchor_points = []
drag_data_x = None
drag_data_y = None

degree = 3

root.mainloop()
