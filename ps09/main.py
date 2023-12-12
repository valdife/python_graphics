import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
import cv2
from PyQt5.QtWidgets import QLineEdit


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        central_widget = QWidget(self)
        layout = QHBoxLayout(central_widget)

        self.image_label = QLabel(self)

        self.menu_container = QWidget(self)
        self.menu_container.setFixedWidth(300)
        self.menu_container.setStyleSheet("background-color: lightgray")

        self.menu_layout = QVBoxLayout(self.menu_container)
        self.menu_layout.setContentsMargins(20, 20, 20, 20)
        self.menu_layout.setSpacing(10)

        # HSV value inputs
        self.lower_hsv_label = QLabel("Lower HSV (H,S,V):")
        self.menu_layout.addWidget(self.lower_hsv_label)
        self.lower_hsv_input = QLineEdit(self)
        self.lower_hsv_input.setPlaceholderText("e.g., 0,0,0")
        self.menu_layout.addWidget(self.lower_hsv_input)

        self.upper_hsv_label = QLabel("Upper HSV (H,S,V):")
        self.menu_layout.addWidget(self.upper_hsv_label)
        self.upper_hsv_input = QLineEdit(self)
        self.upper_hsv_input.setPlaceholderText("e.g., 255,255,255")
        self.menu_layout.addWidget(self.upper_hsv_input)

        # Buttons and labels
        self.load_image_button = QPushButton("Load Image")
        self.load_image_button.clicked.connect(self.load_image)
        self.menu_layout.addWidget(self.load_image_button)

        self.refresh_image_button = QPushButton("Refresh Image")
        self.refresh_image_button.clicked.connect(self.reload_image_fresh)
        self.menu_layout.addWidget(self.refresh_image_button)

        self.detect_color_button = QPushButton("Detect Color")
        self.detect_color_button.clicked.connect(self.detect_color)
        self.menu_layout.addWidget(self.detect_color_button)

        self.error_label = QLabel("No errors found")
        self.error_label.setFixedHeight(50)
        self.menu_layout.addWidget(self.error_label)

        self.image_preview_label = QLabel(self)
        self.menu_layout.addWidget(self.image_preview_label)

        self.color_percentage_label = QLabel(self)
        self.menu_layout.addWidget(self.color_percentage_label)

        # Predefined colors
        self.populate_color_grid()

        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.menu_container)
        splitter.addWidget(self.image_label)
        splitter.setSizes([300, 1920])

        # Default values
        self.lower_default_values = (60, 40, 40)
        self.upper_default_values = (90, 255, 255)

        self.lower_hsv_input.setText(",".join(map(str, self.lower_default_values)))
        self.upper_hsv_input.setText(",".join(map(str, self.upper_default_values)))

        layout.addWidget(splitter)

        self.setCentralWidget(central_widget)
        self.resize(1920, 1080)
        self.showMaximized()
        self.setWindowTitle("Image Viewer")
        self.load_image()
        self.show()

    def load_image(self, file_path=None):
        if not file_path:
            file_path = "kampus-PB-analiza-terenow-zielonych (1).png"
            self.original_file_path = file_path

        if file_path:
            self.image = cv2.imread(file_path)

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

            # Display updated color patch and color percentage
            self.update_color_patch()

    def detect_color(self):
        if self.image is not None:
            lower_hsv_values = self.get_hsv_values(self.lower_hsv_input)
            upper_hsv_values = self.get_hsv_values(self.upper_hsv_input)

            if lower_hsv_values and upper_hsv_values:
                color_mask = self.detect_color_mask(
                    cv2.imread(self.original_file_path),
                    lower_hsv_values,
                    upper_hsv_values,
                )
                self.display_detected_color(color_mask)
                color_percentage = self.calculate_color_percentage(color_mask)
                self.color_percentage_label.setText(
                    f"Color Percentage: {color_percentage:.2f}%"
                )
                self.error_label.setText("")

    def detect_color_mask(self, image, lower_hsv_values, upper_hsv_values):
        # Blur the image
        blurred_image = cv2.GaussianBlur(image, (9, 9), 0)

        # Convert the blurred image to HSV
        hsv_image = cv2.cvtColor(blurred_image, cv2.COLOR_RGB2HSV)

        # Create lower and upper color bounds
        lower_color = np.array(lower_hsv_values)
        upper_color = np.array(upper_hsv_values)

        # Create a color mask
        color_mask = cv2.inRange(hsv_image, lower_color, upper_color)

        # Apply morphology operations
        kernel = np.ones((5, 5), np.uint8)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)

        return color_mask

    def get_hsv_values(self, hsv_input):
        hsv_text = hsv_input.text()
        try:
            hsv_values = list(map(int, hsv_text.split(",")))
            if len(hsv_values) == 3:
                return hsv_values
            else:
                self.error_label.setText("Invalid input. Please use the format H,S,V.")
                return None
        except ValueError:
            self.error_label.setText("Invalid input. Please use the format H,S,V.")
            return None

    def calculate_color_percentage(self, color_mask):
        total_pixels = color_mask.size
        colored_pixels = np.count_nonzero(color_mask)
        percentage = (colored_pixels / total_pixels) * 100
        return percentage

    def display_detected_color(self, color_mask):
        # Apply the color mask to the original image
        color_image = cv2.bitwise_and(self.image, self.image, mask=color_mask)

        # Convert the resulting image to QImage and display it
        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        height, width, channel = color_image.shape
        aspect_ratio = width / height
        label_width = self.image_label.width()
        label_height = self.image_label.height()
        if label_width / aspect_ratio <= label_height:
            new_width = label_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = label_height
            new_width = int(new_height * aspect_ratio)
        color_image = cv2.resize(color_image, (new_width, new_height))
        bytesPerLine = 3 * new_width
        q_image = QImage(
            color_image.data,
            new_width,
            new_height,
            bytesPerLine,
            QImage.Format_RGB888,
        )
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)

    def populate_color_grid(self):
        color_dict_HSV = {
            "black": [[180, 255, 30], [0, 0, 0]],
            "white": [[180, 18, 255], [0, 0, 231]],
            "red": [[180, 255, 255], [159, 50, 70]],
            "mediumseagreen": [[90, 255, 255], [60, 40, 40]],
            "#916B68": [[128, 255, 255], [90, 50, 70]],
            "yellow": [[35, 255, 255], [25, 50, 70]],
            "purple": [[158, 255, 255], [129, 50, 70]],
            "orange": [[24, 255, 255], [10, 50, 70]],
            "gray": [[180, 18, 230], [0, 0, 40]],
        }

        for color_name, hsv_ranges in color_dict_HSV.items():
            button = QPushButton()
            button.setStyleSheet(f"background-color: {color_name}")
            button.clicked.connect(
                lambda _, c=hsv_ranges: self.set_hsv_from_color(c, color_name)
            )
            self.menu_layout.addWidget(button)

    def set_hsv_from_color(self, color_range, color_name):
        self.lower_hsv_input.setText(
            f"{color_range[1][0]},{color_range[1][1]},{color_range[1][2]}"
        )
        self.upper_hsv_input.setText(
            f"{color_range[0][0]},{color_range[0][1]},{color_range[0][2]}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
