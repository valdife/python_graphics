from tkinter import *
import json
from models import Line, Rectangle, Point, Circle


class DrawingApp(Frame):
    def __init__(self, root: Tk) -> None:
        super().__init__()
        self.root = root
        self.initUI()

    def initUI(self) -> None:
        # create all of the first layer containers
        canvas_frame = Frame(self.root, bg='white', width=800, height=425, pady=3)
        interface_frame = Frame(self.root, width=800, height=275, padx=3, pady=3)

        # layout all of the first layer containers
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        canvas_frame.grid(row=0, sticky="ew")
        interface_frame.grid(row=1, sticky="nsew")

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

        load_button = Button(left_frame, text='Load')
        load_button.grid(row=1, column=0, sticky="ew", padx=3, pady=15)

        save_button = Button(left_frame, text='Save')
        save_button.grid(row=2, column=0, sticky="sew", padx=3, pady=15)

        # create widgets for the center frame
        center_frame.grid_columnconfigure(4, weight=1)
        center_frame.grid_rowconfigure(3, weight=1)

        point1_x_label = Label(center_frame, text='Point 1 X')
        point1_x_label.grid(row=0, column=0, sticky="w", padx=3, pady=15)

        point1_x_entry = Entry(center_frame)
        point1_x_entry.grid(row=0, column=1, sticky="ew", padx=3, pady=15)

        point1_y_label = Label(center_frame, text='Point 1 Y')
        point1_y_label.grid(row=0, column=2, sticky="w", padx=3, pady=15)

        point1_y_entry = Entry(center_frame)
        point1_y_entry.grid(row=0, column=3, sticky="ew", padx=3, pady=15)

        point2_x_label = Label(center_frame, text='Point 2 X')
        point2_x_label.grid(row=1, column=0, sticky="w", padx=3, pady=15)

        point2_x_entry = Entry(center_frame)
        point2_x_entry.grid(row=1, column=1, sticky="ew", padx=3, pady=15)

        point2_y_label = Label(center_frame, text='Point 2 Y')
        point2_y_label.grid(row=1, column=2, sticky="w", padx=3, pady=15)

        point2_y_entry = Entry(center_frame)
        point2_y_entry.grid(row=1, column=3, sticky="ew", padx=3, pady=15)

        radius_label = Label(center_frame, text='Radius')
        radius_label.grid(row=2, column=0, sticky="w", padx=3, pady=15)

        radius_entry = Entry(center_frame)
        radius_entry.grid(row=2, column=1, sticky="ew", padx=3, pady=15, columnspan=2)

        # create widgets for the right frame
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(2, weight=1)

        draw_button = Button(right_frame, text='Draw')
        draw_button.grid(row=0, column=0, sticky="ew", padx=3, pady=15)

        clear_button = Button(right_frame, text='Clear')
        clear_button.grid(row=1, column=0, sticky="ew", padx=3, pady=15)

        self.root.mainloop()


if __name__ == '__main__':
    root = Tk()
    root.geometry('{}x{}'.format(800, 600))
    app = DrawingApp(root=root)
    root.mainloop()
