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
        canvas_frame = Frame(self.root, bg='cyan', width=800, height=425, pady=3)
        interface_frame = Frame(self.root, bg='red', width=800, height=275, padx=3, pady=3)

        # layout all of the first layer containers
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        canvas_frame.grid(row=0, sticky="ew")
        interface_frame.grid(row=1, sticky="nsew")

        # create the containers for the second layer in the interface frame
        left_frame = Frame(interface_frame, bg='blue', width=200, height=275, pady=3)
        center_frame = Frame(interface_frame, bg='yellow', width=400, height=275, padx=3, pady=3)
        right_frame = Frame(interface_frame, bg='green', width=200, height=275, padx=3, pady=3)

        # layout the widgets in the interface_frame
        interface_frame.grid_rowconfigure(3, weight=1)
        interface_frame.grid_columnconfigure(0, weight=1)

        left_frame.grid(row=0, column=0, sticky="ns")
        center_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid(row=0, column=2, sticky="ns")

        self.root.mainloop()


if __name__ == '__main__':
    root = Tk()
    root.geometry('{}x{}'.format(800, 600))
    app = DrawingApp(root=root)
    root.mainloop()
