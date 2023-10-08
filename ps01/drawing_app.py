from tkinter import *
from actions import deserialize_from_dict, draw_from_input, clear_canvas, file_save, load_from_file


serialized_shapes = []


class DrawingApp(Frame):
    def __init__(self, root: Tk) -> None:
        super().__init__()
        self.root = root
        self.initUI()

    def initUI(self) -> None:
        serialized_shapes = []

        # create all of the first layer containers
        canvas_frame = Frame(self.root, bg='white', width=800, height=425, pady=3)
        interface_frame = Frame(self.root, width=800, height=275, padx=3, pady=3)

        # layout all of the first layer containers
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        canvas_frame.grid(row=0, sticky="ew")
        interface_frame.grid(row=1, sticky="nsew")

        # create canvas in canvas_frame
        canvas = Canvas(canvas_frame, bg='white', width=800, height=425)
        canvas.grid(row=0, column=0, sticky="nsew")

        # create the containers for the second layer in the interface frame
        left_frame = Frame(interface_frame, width=100, height=275, pady=3)
        center_frame = Frame(interface_frame, width=500, height=275, padx=3, pady=3)
        right_frame = Frame(interface_frame, width=200, height=275, padx=3, pady=3)

        # layout the widgets in the interface_frame
        interface_frame.grid_rowconfigure(0, weight=1)
        interface_frame.grid_columnconfigure(3, weight=1)

        left_frame.grid(row=0, column=0, sticky='nsw', padx=30)
        center_frame.grid(row=0, column=1, sticky='nsew')
        right_frame.grid(row=0, column=3, sticky='nse')

        # create widgets for the left frame
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(3, weight=1)

        shape_option_value = StringVar(left_frame, 'Line')
        shape_option_menu = OptionMenu(left_frame, shape_option_value, 'Line', 'Rectangle', 'Circle')
        shape_option_menu.grid(row=0, column=0, sticky="new", padx=3, pady=15)

        load_button = Button(left_frame, text='Load', command=lambda: load_from_file(canvas=canvas))
        load_button.grid(row=1, column=0, sticky="ew", padx=3, pady=15)

        save_button = Button(left_frame, text='Save', command=lambda: file_save(serialized_shapes))
        save_button.grid(row=2, column=0, sticky="sew", padx=3, pady=15)

        # create widgets for the center frame
        center_frame.grid_columnconfigure(4, weight=1)
        center_frame.grid_rowconfigure(3, weight=1)

        point1_x_label = Label(center_frame, text='Point 1 X')
        point1_x_label.grid(row=0, column=0, sticky="w", padx=3, pady=15)

        point1_x = StringVar(center_frame, value='0')
        point1_x_entry = Entry(center_frame, textvariable=point1_x)
        point1_x_entry.grid(row=0, column=1, sticky="ew", padx=3, pady=15)

        point1_y_label = Label(center_frame, text='Point 1 Y')
        point1_y_label.grid(row=0, column=2, sticky="w", padx=3, pady=15)

        point1_y = StringVar(center_frame, value='0')
        point1_y_entry = Entry(center_frame, textvariable=point1_y)
        point1_y_entry.grid(row=0, column=3, sticky="ew", padx=3, pady=15)

        point2_x_label = Label(center_frame, text='Point 2 X')
        point2_x_label.grid(row=1, column=0, sticky="w", padx=3, pady=15)

        point2_x = StringVar(center_frame, value='0')
        point2_x_entry = Entry(center_frame, textvariable=point2_x)
        point2_x_entry.grid(row=1, column=1, sticky="ew", padx=3, pady=15)

        point2_y_label = Label(center_frame, text='Point 2 Y')
        point2_y_label.grid(row=1, column=2, sticky="w", padx=3, pady=15)

        point2_y = StringVar(center_frame, value='0')
        point2_y_entry = Entry(center_frame, textvariable=point2_y)
        point2_y_entry.grid(row=1, column=3, sticky="ew", padx=3, pady=15)

        radius_label = Label(center_frame, text='Radius')
        radius_label.grid(row=2, column=0, sticky="w", padx=3, pady=15)

        radius = StringVar(center_frame, value='0')
        radius_entry = Entry(center_frame, textvariable=radius)
        radius_entry.grid(row=2, column=1, sticky="ew", padx=3, pady=15, columnspan=2)

        # create widgets for the right frame
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(2, weight=1)

        draw_button = Button(
            master=right_frame,
            text='Draw',
            command=lambda: draw_from_input(
                canvas,
                shape_option_value.get(),
                point1_x.get(),
                point1_y.get(),
                point2_x.get(),
                point2_y.get(),
                radius.get(),
                serialized_shapes
            )
        )
        draw_button.grid(row=0, column=0, sticky="ew", padx=3, pady=15)

        clear_button = Button(right_frame, text='Clear', command=lambda: clear_canvas(canvas))
        clear_button.grid(row=1, column=0, sticky="ew", padx=3, pady=15)

        self.root.mainloop()


if __name__ == '__main__':
    root = Tk()
    root.geometry('{}x{}'.format(800, 600))
    app = DrawingApp(root=root)
    root.mainloop()
