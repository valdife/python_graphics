import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
import cv2
import pyqtgraph as pg
import math
from PyQt5.QtWidgets import QLineEdit
from scipy.signal import convolve2d

kernel = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
hit_kernel = [[1, 0], [1, 1]]
miss_kernel = [[0, 0], [0, 0]]


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        central_widget = QWidget(self)
        layout = QHBoxLayout(central_widget)

        self.image_label = QLabel(self)

        self.menu_container = QWidget(self)
        self.menu_container.setFixedWidth(200)
        self.menu_container.setStyleSheet("background-color: lightgray")

        self.menu_layout = QGridLayout(self.menu_container)
        self.menu_layout.setContentsMargins(20, 20, 20, 20)
        self.menu_layout.setSpacing(10)
        self.menu_layout.setRowStretch(4, 1)

        self.load_image_button = QPushButton("Load Image")
        self.load_image_button.clicked.connect(self.load_image)
        self.menu_layout.addWidget(self.load_image_button, 0, 0)

        self.refresh_image_button = QPushButton("Refresh Image")
        self.refresh_image_button.clicked.connect(self.reload_image_fresh)
        self.menu_layout.addWidget(self.refresh_image_button, 1, 0)

        self.dilatation_button = QPushButton("Dilation")
        self.dilatation_button.clicked.connect(self.dilation)
        self.menu_layout.addWidget(self.dilatation_button, 2, 0)

        self.erosion_button = QPushButton("Erosion")
        self.erosion_button.clicked.connect(self.erosion)
        self.menu_layout.addWidget(self.erosion_button, 3, 0)

        self.opening_button = QPushButton("Opening")
        self.opening_button.clicked.connect(self.opening)
        self.menu_layout.addWidget(self.opening_button, 4, 0)

        self.closing_button = QPushButton("Closing")
        self.closing_button.clicked.connect(self.closing)
        self.menu_layout.addWidget(self.closing_button, 6, 0)

        self.hitormiss_button = QPushButton("Hit-or-Miss")
        self.hitormiss_button.clicked.connect(self.hitormiss)
        self.menu_layout.addWidget(self.hitormiss_button, 7, 0)

        self.matrix_label = QLabel('Write matrix below like "0 1 1 1 ..."')
        self.matrix_label.setFixedHeight(50)
        self.menu_layout.addWidget(self.matrix_label, 8, 0)

        self.matrix_textbox = QTextEdit()
        self.matrix_textbox.setFixedHeight(100)
        self.menu_layout.addWidget(self.matrix_textbox, 9, 0)

        self.save_matrix_button = QPushButton("Save matrix")
        self.save_matrix_button.clicked.connect(lambda: self.save_matrix("kernel"))
        self.menu_layout.addWidget(self.save_matrix_button, 10, 0)

        self.save_matrix_button = QPushButton("Save hit matrix")
        self.save_matrix_button.clicked.connect(lambda: self.save_matrix("hit"))
        self.menu_layout.addWidget(self.save_matrix_button, 11, 0)

        self.save_matrix_button = QPushButton("Save miss matrix")
        self.save_matrix_button.clicked.connect(lambda: self.save_matrix("miss"))
        self.menu_layout.addWidget(self.save_matrix_button, 12, 0)

        self.display_matrix_button = QPushButton("Display matrix")
        self.display_matrix_button.clicked.connect(
            lambda: self.display_matrix("kernel")
        )
        self.menu_layout.addWidget(self.display_matrix_button, 13, 0)

        self.display_matrix_button = QPushButton("Display hit matrix")
        self.display_matrix_button.clicked.connect(lambda: self.display_matrix("hit"))
        self.menu_layout.addWidget(self.display_matrix_button, 14, 0)

        self.display_matrix_button = QPushButton("Display miss matrix")
        self.display_matrix_button.clicked.connect(lambda: self.display_matrix("miss"))
        self.menu_layout.addWidget(self.display_matrix_button, 15, 0)

        self.matrix_output_textbox = QTextEdit()
        self.matrix_output_textbox.setFixedHeight(100)
        self.menu_layout.addWidget(self.matrix_output_textbox, 16, 0)

        self.error_label = QLabel("No errors found")
        self.error_label.setFixedHeight(50)
        self.menu_layout.addWidget(self.error_label, 20, 0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.menu_container)
        splitter.addWidget(self.image_label)
        splitter.setSizes([200, 1920])

        layout.addWidget(splitter)

        formatted_kernel = "\n".join([" ".join(map(str, row)) for row in kernel])
        self.matrix_output_textbox.setPlainText(formatted_kernel)

        self.setCentralWidget(central_widget)
        self.resize(1920, 1080)
        self.showMaximized()
        self.setWindowTitle("Image Viewer")
        self.load_image()
        self.show()

    def load_image(self, file_path=None):
        if not file_path:
            # options = QFileDialog.Options()
            # options |= QFileDialog.ReadOnly
            # file_path, _ = QFileDialog.getOpenFileName(
            #     self, "Open Image File", "", "Image Files (*.ppm *.jpeg *.jpg);;All Files (*)", options=options)
            file_path = "i01_oig-1.jpg"
            self.original_file_path = file_path

        if file_path:
            self.image = cv2.imread(self.original_file_path)

            if self.image is not None:
                self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                height, width, channel = self.image.shape
                aspect_ratio = width / height
                label_width = self.image_label.width()
                label_height = self.image_label.height()
                if label_width / aspect_ratio <= label_height:
                    new_width = label_width
                    new_height = int(new_width / aspect_ratio)
                else:
                    new_height = label_height
                    new_width = int(new_height * aspect_ratio)
                tempimage = cv2.resize(self.image, (new_width, new_height))
                bytesPerLine = 3 * new_width
                self.q_image = QImage(
                    tempimage.data,
                    new_width,
                    new_height,
                    bytesPerLine,
                    QImage.Format_RGB888,
                )
                pixmap = QPixmap.fromImage(self.q_image)
                self.image_label.setPixmap(pixmap)
                self.setWindowTitle(f"Image Viewer - {file_path}")
            else:
                print("Failed to load the image.")
        else:
            print("No image selected.")

    def reload_image_fresh(self):
        self.load_image(self.original_file_path)

    def reload_image(self):
        if self.image is not None:
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            height, width, channel = self.image.shape
            aspect_ratio = width / height
            label_width = self.image_label.width()
            label_height = self.image_label.height()
            if label_width / aspect_ratio <= label_height:
                new_width = label_width
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = label_height
                new_width = int(new_height * aspect_ratio)
            tempimage = cv2.resize(self.image, (new_width, new_height))
            bytesPerLine = 3 * new_width
            self.q_image = QImage(
                tempimage.data,
                new_width,
                new_height,
                bytesPerLine,
                QImage.Format_RGB888,
            )
            pixmap = QPixmap.fromImage(self.q_image)
            self.image_label.setPixmap(pixmap)

    def custom_erode(self, image, kernel):
        # Get the size of the kernel
        k_rows, k_cols = kernel.shape

        # Get the height and width of the image
        rows, cols = image.shape

        # Create an empty result image with an extended border
        result_image = np.zeros(
            (rows + k_rows - 1, cols + k_cols - 1), dtype=image.dtype
        )

        # Place the original image in the center of the result image
        result_image[
            k_rows // 2 : k_rows // 2 + rows, k_cols // 2 : k_cols // 2 + cols
        ] = image

        # Iterate over each pixel in the original image
        for i in range(rows):
            for j in range(cols):
                # Apply erosion operation
                region = result_image[i : i + k_rows, j : j + k_cols]
                image[i, j] = np.min(region * kernel)

        return image

    def custom_dilate(self, image, kernel):
        # Get the size of the kernel
        k_rows, k_cols = kernel.shape

        # Get the height and width of the image
        rows, cols = image.shape

        # Create an empty result image with an extended border
        result_image = np.zeros(
            (rows + k_rows - 1, cols + k_cols - 1), dtype=image.dtype
        )

        # Place the original image in the center of the result image
        result_image[
            k_rows // 2 : k_rows // 2 + rows, k_cols // 2 : k_cols // 2 + cols
        ] = image

        # Iterate over each pixel in the original image
        for i in range(rows):
            for j in range(cols):
                # Apply dilation operation
                region = result_image[i : i + k_rows, j : j + k_cols]
                image[i, j] = np.max(region * kernel)

        return image

    def dilation(self):
        global kernel
        print(type(self.image))
        print(type(self.q_image))

        grayscale_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)

        # Create a kernel using NumPy array
        kernel_np = np.array(kernel, dtype=np.uint8)

        # Get the size of the kernel
        k_rows, k_cols = kernel_np.shape

        # Create an image with extended borders
        border_size = (k_rows // 2, k_cols // 2)
        grayscale_image_padded = cv2.copyMakeBorder(
            grayscale_image,
            top=border_size[0],
            bottom=border_size[0],
            left=border_size[1],
            right=border_size[1],
            borderType=cv2.BORDER_WRAP,
        )

        # Perform erosion using self.custom_erode
        eroded_image_padded = self.custom_dilate(grayscale_image_padded, kernel_np)

        # Crop the result to remove the extended borders
        eroded_image = eroded_image_padded[
            border_size[0] : -border_size[0], border_size[1] : -border_size[1]
        ]

        # Convert the result to RGB format for display
        eroded_image_rgb = cv2.cvtColor(eroded_image, cv2.COLOR_GRAY2RGB)

        # Update the displayed image
        height, width, channel = eroded_image_rgb.shape
        bytesPerLine = 3 * width
        self.image = eroded_image_rgb
        self.reload_image()

    def erosion(self):
        global kernel
        print(type(self.image))
        print(type(self.q_image))

        grayscale_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)

        # Create a kernel using NumPy array
        kernel_np = np.array(kernel, dtype=np.uint8)

        # Get the size of the kernel
        k_rows, k_cols = kernel_np.shape

        # Create an image with extended borders
        border_size = (k_rows // 2, k_cols // 2)
        grayscale_image_padded = cv2.copyMakeBorder(
            grayscale_image,
            top=border_size[0],
            bottom=border_size[0],
            left=border_size[1],
            right=border_size[1],
            borderType=cv2.BORDER_WRAP,
        )

        # Perform erosion using self.custom_erode
        eroded_image_padded = self.custom_erode(grayscale_image_padded, kernel_np)

        # Crop the result to remove the extended borders
        eroded_image = eroded_image_padded[
            border_size[0] : -border_size[0], border_size[1] : -border_size[1]
        ]

        # Convert the result to RGB format for display
        eroded_image_rgb = cv2.cvtColor(eroded_image, cv2.COLOR_GRAY2RGB)

        # Update the displayed image
        height, width, channel = eroded_image_rgb.shape
        bytesPerLine = 3 * width
        self.image = eroded_image_rgb
        self.reload_image()

    def opening(self):
        global kernel

        # Convert the image to grayscale
        grayscale_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)

        # Create a kernel using NumPy array
        kernel_np = np.array(kernel, dtype=np.uint8)

        # Get the size of the kernel
        k_rows, k_cols = kernel_np.shape

        # Create an image with extended borders
        border_size = (k_rows // 2, k_cols // 2)
        grayscale_image_padded = cv2.copyMakeBorder(
            grayscale_image,
            top=border_size[0],
            bottom=border_size[0],
            left=border_size[1],
            right=border_size[1],
            borderType=cv2.BORDER_WRAP,
        )

        # Perform erosion using self.custom_erode
        eroded_image_padded = self.custom_erode(grayscale_image_padded, kernel_np)

        # Perform dilation using self.custom_dilate
        opened_image_padded = self.custom_dilate(eroded_image_padded, kernel_np)

        # Crop the result to remove the extended borders
        opened_image = opened_image_padded[
            border_size[0] : -border_size[0], border_size[1] : -border_size[1]
        ]

        # Convert the result to RGB format for display
        opened_image_rgb = cv2.cvtColor(opened_image, cv2.COLOR_GRAY2RGB)

        # Update the displayed image
        height, width, channel = opened_image_rgb.shape
        bytesPerLine = 3 * width
        self.image = opened_image_rgb
        self.reload_image()

    def closing(self):
        global kernel

        # Convert the image to grayscale
        grayscale_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)

        # Create a kernel using NumPy array
        kernel_np = np.array(kernel, dtype=np.uint8)

        # Get the size of the kernel
        k_rows, k_cols = kernel_np.shape

        # Create an image with extended borders
        border_size = (k_rows // 2, k_cols // 2)
        grayscale_image_padded = cv2.copyMakeBorder(
            grayscale_image,
            top=border_size[0],
            bottom=border_size[0],
            left=border_size[1],
            right=border_size[1],
            borderType=cv2.BORDER_WRAP,
        )

        # Perform erosion using self.custom_erode
        eroded_image_padded = self.custom_dilate(grayscale_image_padded, kernel_np)

        # Perform dilation using self.custom_dilate
        opened_image_padded = self.custom_erode(eroded_image_padded, kernel_np)

        # Crop the result to remove the extended borders
        opened_image = opened_image_padded[
            border_size[0] : -border_size[0], border_size[1] : -border_size[1]
        ]

        # Convert the result to RGB format for display
        opened_image_rgb = cv2.cvtColor(opened_image, cv2.COLOR_GRAY2RGB)

        # Update the displayed image
        height, width, channel = opened_image_rgb.shape
        bytesPerLine = 3 * width
        self.image = opened_image_rgb
        self.reload_image()

    def hitormiss(self):
        global kernel, hit_kernel, miss_kernel

        grayscale_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
        _, binary_image = cv2.threshold(grayscale_image, 128, 255, cv2.THRESH_BINARY)
        hit_kernel_np = np.array(hit_kernel, dtype=np.uint8)
        miss_kernel_np = ~hit_kernel_np
        eroded_image_hit = self.custom_erode(binary_image, hit_kernel_np)
        eroded_image_miss_inv = self.custom_erode(binary_image, miss_kernel_np)
        hitormiss_result = cv2.bitwise_and(eroded_image_hit, eroded_image_miss_inv)
        hitormiss_result_rgb = cv2.cvtColor(hitormiss_result, cv2.COLOR_GRAY2RGB)
        height, width, channel = hitormiss_result_rgb.shape
        bytesPerLine = 3 * width
        self.image = hitormiss_result_rgb
        self.reload_image()

    def group_array(self, original_array, group_size):
        # Convert strings to numbers
        original_array = [int(item) for item in original_array]

        # Group elements based on the desired size
        grouped_array = [
            original_array[i : i + group_size]
            for i in range(0, len(original_array), group_size)
        ]

        return grouped_array

    def save_matrix(self, type):
        global kernel, hit_kernel, miss_kernel
        matrix_text = self.matrix_textbox.toPlainText()
        matrix_rows = matrix_text.strip().split(" ")
        num_rows = len(matrix_rows)
        square_root = math.sqrt(num_rows)

        if square_root != int(square_root):
            print("Invalid matrix size.")
            self.error_label.setText("Invalid matrix size.")
            return
        else:
            if type == "kernel":
                kernel = self.group_array(matrix_rows, int(square_root))
                self.display_matrix(type)
            elif type == "hit":
                hit_kernel = self.group_array(matrix_rows, int(square_root))
                self.display_matrix(type)
            elif type == "miss":
                miss_kernel = self.group_array(matrix_rows, int(square_root))
                self.display_matrix(type)
        if num_rows == 0:
            return

        # Display the matrix in the output textbox
        formatted_kernel = "\n".join([" ".join(map(str, row)) for row in kernel])
        self.matrix_output_textbox.setPlainText(formatted_kernel)

    def display_matrix(self, type):
        global kernel, hit_kernel, miss_kernel
        if type == "kernel":
            formatted_kernel = "\n".join([" ".join(map(str, row)) for row in kernel])
            self.matrix_output_textbox.setPlainText(formatted_kernel)
            self.error_label.setText("Displaying Kernel")
        elif type == "hit":
            formatted_kernel = "\n".join(
                [" ".join(map(str, row)) for row in hit_kernel]
            )
            self.matrix_output_textbox.setPlainText(formatted_kernel)
            self.error_label.setText("Displaying Hit Kernel")
        elif type == "miss":
            formatted_kernel = "\n".join(
                [" ".join(map(str, row)) for row in miss_kernel]
            )
            self.matrix_output_textbox.setPlainText(formatted_kernel)
            self.error_label.setText("Displaying Miss Kernel")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
