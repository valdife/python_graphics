import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
import cv2
from functools import partial
import time
from scipy.signal import convolve2d

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

        menu_layout = QGridLayout(self.menu_container)
        menu_layout.setContentsMargins(20, 20, 20, 20)
        menu_layout.setSpacing(10)
        menu_layout.setRowStretch(4, 1)

        # * Load buttons
        load_image_button = QPushButton("Load Image")
        load_image_button.clicked.connect(self.load_image)
        menu_layout.addWidget(load_image_button,0,0)

        refresh_image_button = QPushButton("Refresh Image")
        refresh_image_button.clicked.connect(self.reload_image_fresh)
        refresh_image_button
        menu_layout.addWidget(refresh_image_button,1,0)


        # * RGB input fields
        rgb_widget = QWidget()
        rgb_layout = QGridLayout(rgb_widget)
        rgb_layout.setContentsMargins(0,0,0,0)
        rgb_layout.setSpacing(0)
        self.red_text = QLineEdit()
        self.red_text.setFixedWidth(50)
        self.red_text.setFixedHeight(30)
        self.red_text.setStyleSheet("border-color: red; border-width: 2px; border-style: solid; border-radius:5px")
        self.red_text.setValidator(QDoubleValidator(self))
        self.red_text.setText("0")
        self.green_text = QLineEdit()
        self.green_text.setFixedWidth(50)
        self.green_text.setFixedHeight(30)
        self.green_text.setStyleSheet("border-color: green; border-width: 2px; border-style: solid; border-radius:5px")
        self.green_text.setValidator(QDoubleValidator(self))
        self.green_text.setText("0")
        self.blue_text = QLineEdit()
        self.blue_text.setFixedWidth(50)
        self.blue_text.setFixedHeight(30)
        self.blue_text.setStyleSheet("border-color: blue; border-width: 2px; border-style: solid; border-radius:5px")
        self.blue_text.setValidator(QDoubleValidator(self))
        self.blue_text.setText("0")


        rgb_layout.addWidget(self.red_text,0,0)
        rgb_layout.addWidget(self.green_text,0,1)
        rgb_layout.addWidget(self.blue_text,0,2)
        rgb_widget.setStyleSheet("max-height: 30px")
        menu_layout.addWidget(rgb_widget,2,0)

        # * Basic calculations buttons
        add_button = QPushButton("Addition")
        add_button.clicked.connect(self.add_rgb)
        menu_layout.addWidget(add_button,3,0)
        subtract_button = QPushButton("Subtraction")
        subtract_button.clicked.connect(self.subtract_rgb)
        menu_layout.addWidget(subtract_button,4,0)
        multiply_button = QPushButton("Multiplication")
        multiply_button.clicked.connect(self.multiply_rgb)
        menu_layout.addWidget(multiply_button,5,0)
        divide_button = QPushButton("Division")
        divide_button.clicked.connect(self.divide_rgb)
        menu_layout.addWidget(divide_button,6,0)

        # * Brightness buttons
        self.slider = QSlider()
        self.slider.setOrientation(1)  # Vertical orientation
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(0)  # Set the base value to 0%
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setTickInterval(10)
        menu_layout.addWidget(self.slider,7,0)
        self.slider.valueChanged.connect(self.slider_value_changed)
        self.label = QLabel("0%")
        self.label.setFixedHeight(50)
        menu_layout.addWidget(self.label, 8, 0)

        self.brightness_up_button=QPushButton("Brightness up")
        self.brightness_up_button.clicked.connect(partial(self.brightness_rgb, "up"))
        self.brightness_down_button=QPushButton("Brightness down")
        self.brightness_down_button.clicked.connect(partial(self.brightness_rgb, "down"))
        menu_layout.addWidget(self.brightness_up_button,9,0)
        menu_layout.addWidget(self.brightness_down_button,10,0)

        # * Grayscale buttons
        self.grayscale_button_even = QPushButton("Grayscale even")
        self.grayscale_button_even.clicked.connect(partial(self.grayscale_rgb, "even"))
        self.grayscale_button_ratio = QPushButton("Grayscale ratio")
        self.grayscale_button_ratio.clicked.connect(partial(self.grayscale_rgb, "ratio"))
        menu_layout.addWidget(self.grayscale_button_even,11,0)
        menu_layout.addWidget(self.grayscale_button_ratio,12,0)

        # * Filters buttons
        self.smoothing_button = QPushButton("Smoothing")
        self.smoothing_button.clicked.connect(self.smoothing)
        self.median_button = QPushButton("Median")
        self.median_button.clicked.connect(self.median)
        self.edge_detection_button = QPushButton("Edge detection")
        self.edge_detection_button.clicked.connect(self.edge_detection)
        self.high_pass_button = QPushButton("High pass")
        self.high_pass_button.clicked.connect(self.high_pass)
        self.gaussian_blur_button = QPushButton("Gaussian blur")
        self.gaussian_blur_button.clicked.connect(self.gaussian_blur)
        self.mask_veave_button = QPushButton("Mask veave")
        self.mask_veave_button.clicked.connect(self.mask_veave)

        self.filters_label = QLabel("Filters:")
        self.filters_label.setFixedHeight(50)
        menu_layout.addWidget(self.filters_label, 13, 0)

        menu_layout.addWidget(self.smoothing_button,14,0)
        menu_layout.addWidget(self.median_button,15,0)
        menu_layout.addWidget(self.edge_detection_button,16,0)
        menu_layout.addWidget(self.high_pass_button,17,0)
        menu_layout.addWidget(self.gaussian_blur_button,18,0)
        menu_layout.addWidget(self.mask_veave_button,19,0)

        self.error_label = QLabel("No errors found")
        self.error_label.setFixedHeight(50)
        menu_layout.addWidget(self.error_label, 20, 0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.menu_container)
        splitter.addWidget(self.image_label)
        splitter.setSizes([200, 1920])

        layout.addWidget(splitter)

        self.setCentralWidget(central_widget)
        self.resize(1920,1080)
        self.showMaximized()
        self.setWindowTitle("XD?")
        self.show()


    def load_image(self, file_path=None):

        if not file_path:
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Image File", "", "Image Files (*.ppm *.jpeg *.jpg);;All Files (*)", options=options)
            self.original_file_path = file_path

        if file_path:
            # Load the image using OpenCV
            self.image = cv2.imread(self.original_file_path)

            if self.image is not None:
                # Convert BGR image to RGB
                self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

                # Get the dimensions of the image
                height, width, channel = self.image.shape

                # Calculate the aspect ratio to scale the image
                aspect_ratio = width / height

                # Get the size of self.image_label
                label_width = self.image_label.width()
                label_height = self.image_label.height()

                # Determine the new size of the image while maintaining the aspect ratio
                if label_width / aspect_ratio <= label_height:
                    new_width = label_width
                    new_height = int(new_width / aspect_ratio)
                else:
                    new_height = label_height
                    new_width = int(new_height * aspect_ratio)

                # Resize the image
                self.image = cv2.resize(self.image, (new_width, new_height))

                # Create a QImage from the NumPy array
                bytesPerLine = 3 * new_width
                self.q_image = QImage(self.image.data, new_width, new_height, bytesPerLine, QImage.Format_RGB888)

                # Display the image
                pixmap = QPixmap.fromImage(self.q_image)
                self.image_label.setPixmap(pixmap)
                self.setWindowTitle(f"Image Viewer - {file_path}")
            else:
                print("Failed to load the image.")
        else:
            print("No image selected.")


    def reload_image_fresh(self):
        # Reload the original image
        self.load_image(self.original_file_path)

    def reload_image(self):
        # Reload the modified image
        pixmap = QPixmap.fromImage(self.q_image)
        self.image_label.setPixmap(pixmap)

    def add_rgb(self):
        red_input = int(self.red_text.text())
        green_input = int(self.green_text.text())
        blue_input = int(self.blue_text.text())


        img_data = np.array(self.image)  # Convert the original image to a NumPy array
        img_data = img_data.astype(np.int32)  # Convert the data type to 32-bit integers

        # Add the RGB values to the image using NumPy operations
        img_data[:, :, 0] = np.minimum(255, img_data[:, :, 0] + red_input)
        img_data[:, :, 1] = np.minimum(255, img_data[:, :, 1] + green_input)
        img_data[:, :, 2] = np.minimum(255, img_data[:, :, 2] + blue_input)

        # Convert back to 8-bit integer type
        img_data = np.clip(img_data, 0, 255).astype(np.uint8)
        self.image = img_data

        # Convert the NumPy array back to a QImage
        height, width, channel = img_data.shape
        bytesPerLine = 3 * width
        self.q_image = QImage(img_data.data, width, height, bytesPerLine, QImage.Format_RGB888)

        self.reload_image()

    def subtract_rgb(self):
        red_input = int(self.red_text.text())
        green_input = int(self.green_text.text())
        blue_input = int(self.blue_text.text())


        img_data = np.array(self.image)  # Convert the original image to a NumPy array
        img_data = img_data.astype(np.int32)  # Convert the data type to 32-bit integers

        # Add the RGB values to the image using NumPy operations
        img_data[:, :, 0] = np.maximum(0, img_data[:, :, 0] - red_input)
        img_data[:, :, 1] = np.maximum(0, img_data[:, :, 1] - green_input)
        img_data[:, :, 2] = np.maximum(0, img_data[:, :, 2] - blue_input)

        # Convert back to 8-bit integer type
        img_data = np.clip(img_data, 0, 255).astype(np.uint8)
        self.image = img_data

        # Convert the NumPy array back to a QImage
        height, width, channel = img_data.shape
        bytesPerLine = 3 * width
        self.q_image = QImage(img_data.data, width, height, bytesPerLine, QImage.Format_RGB888)

        self.reload_image()

    def multiply_rgb(self):
        red_input = float(self.red_text.text())
        green_input = float(self.green_text.text())
        blue_input = float(self.blue_text.text())


        img_data = np.array(self.image)  # Convert the original image to a NumPy array
        img_data = img_data.astype(np.int32)  # Convert the data type to 32-bit integers

        # Add the RGB values to the image using NumPy operations
        img_data[:, :, 0] = np.minimum(255, img_data[:, :, 0] * red_input)
        img_data[:, :, 1] = np.minimum(255, img_data[:, :, 1] * green_input)
        img_data[:, :, 2] = np.minimum(255, img_data[:, :, 2] * blue_input)


        # Convert back to 8-bit integer type
        img_data = np.clip(img_data, 0, 255).astype(np.uint8)
        self.image = img_data

        # Convert the NumPy array back to a QImage
        height, width, channel = img_data.shape
        bytesPerLine = 3 * width
        self.q_image = QImage(img_data.data, width, height, bytesPerLine, QImage.Format_RGB888)

        self.reload_image()

    def divide_rgb(self):
        red_input = float(self.red_text.text())
        green_input = float(self.green_text.text())
        blue_input = float(self.blue_text.text())

        img_data = np.array(self.image)  # Convert the original image to a NumPy array
        img_data = img_data.astype(np.int32)  # Convert the data type to 32-bit integers

        # Add the RGB values to the image using NumPy operations
        img_data[:, :, 0] = np.maximum(0, img_data[:, :, 0] / red_input)
        img_data[:, :, 1] = np.maximum(0, img_data[:, :, 1] / green_input)
        img_data[:, :, 2] = np.maximum(0, img_data[:, :, 2] / blue_input)

        # Convert back to 8-bit integer type
        img_data = np.clip(img_data, 0, 255).astype(np.uint8)
        self.image = img_data

        # Convert the NumPy array back to a QImage
        height, width, channel = img_data.shape
        bytesPerLine = 3 * width
        self.q_image = QImage(img_data.data, width, height, bytesPerLine, QImage.Format_RGB888)

        self.reload_image()

    def slider_value_changed(self,value):
        percentage = value
        self.label.setText(f"{percentage}%")

    def brightness_rgb(self, direction):
        brightness_input = int(self.slider.value())
        brightness_input = float(brightness_input)/100

        img_data = np.array(self.image)  # Convert the original image to a NumPy array
        img_data = img_data.astype(np.int32)  # Convert the data type to 32-bit integers

        # Add the RGB values to the image using NumPy operations
        if direction == "up":
            img_data[:, :, 0] = (255 - img_data[:, :, 0])*brightness_input + img_data[:, :, 0]
            img_data[:, :, 1] = (255 - img_data[:, :, 1])*brightness_input + img_data[:, :, 1]
            img_data[:, :, 2] = (255 - img_data[:, :, 2])*brightness_input + img_data[:, :, 2]
        elif direction == "down":
            img_data[:, :, 0] = img_data[:, :, 0] - img_data[:, :, 0] * brightness_input
            img_data[:, :, 1] = img_data[:, :, 1] - img_data[:, :, 1] * brightness_input
            img_data[:, :, 2] = img_data[:, :, 2] - img_data[:, :, 2] * brightness_input

        img_data = np.clip(img_data, 0, 255).astype(np.uint8)
        self.image = img_data

        # Convert the NumPy array back to a QImage
        height, width, channel = img_data.shape
        bytesPerLine = 3 * width
        self.q_image = QImage(img_data.data, width, height, bytesPerLine, QImage.Format_RGB888)

        self.reload_image()

    def grayscale_rgb(self,ratio):
        img_data = np.array(self.image)  # Convert the original image to a NumPy array
        img_data = img_data.astype(np.int32)  # Convert the data type to 32-bit integers

        if ratio == "even":
            average_rgb_value = (img_data[:, :, 0]*0.33 + img_data[:, :, 1]*0.33 + img_data[:, :, 2]*0.33) / 3
            img_data[:, :, 0] = average_rgb_value
            img_data[:, :, 1] = average_rgb_value
            img_data[:, :, 2] = average_rgb_value

        if ratio == "ratio":
            average_rgb_value = (img_data[:, :, 0]*0.299 + img_data[:, :, 1]*0.587 + img_data[:, :, 2]*0.114) / 3
            img_data[:, :, 0] = average_rgb_value
            img_data[:, :, 1] = average_rgb_value
            img_data[:, :, 2] = average_rgb_value

        img_data = np.clip(img_data, 0, 255).astype(np.uint8)
        self.image = img_data

        # Convert the NumPy array back to a QImage
        height, width, channel = img_data.shape
        bytesPerLine = 3 * width
        self.q_image = QImage(img_data.data, width, height, bytesPerLine, QImage.Format_RGB888)

        self.reload_image()


    from scipy.signal import convolve2d

    # ...

    def smoothing(self):
        self.error_label.setText("Wykonywana funkcja: smoothing")
        start_time = time.time()
        kernel = np.array([[1, 1, 1],
                           [1, 1, 1],
                           [1, 1, 1]]) / 9  # Tworzenie kernela do filtru wygładzającego

        img_data = np.array(self.image)
        img_data = img_data.astype(np.int32)

        # Zastosowanie filtra wygładzającego
        smoothed_img_data = np.zeros_like(img_data)
        for c in range(3):
            smoothed_img_data[:, :, c] = convolve2d(img_data[:, :, c], kernel, mode='same', boundary='wrap')

        img_data = np.clip(smoothed_img_data, 0, 255).astype(np.uint8)
        self.image = img_data

        height, width, channel = img_data.shape
        bytesPerLine = 3 * width
        self.image = smoothed_img_data
        self.q_image = QImage(img_data.data, width, height, bytesPerLine, QImage.Format_RGB888)
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.error_label.setText(f"Czas: {elapsed_time:.2f}s")
        self.reload_image()

    def median(self):
        self.error_label.setText("Wykonywana funkcja: median")
        start_time = time.time()
        img_data = np.array(self.image)
        img_data = img_data.astype(np.int32)

        # Zastosowanie filtra medianowego z rozmiarem kernela 3x3
        median_img_data = np.zeros_like(img_data)

        for c in range(3):
            channel = img_data[:, :, c]
            median_channel = self.apply_median_filter(channel)

            median_img_data[:, :, c] = median_channel

        img_data = np.clip(median_img_data, 0, 255).astype(np.uint8)
        self.image = img_data

        height, width, channel = img_data.shape
        bytesPerLine = 3 * width
        self.q_image = QImage(img_data.data, width, height, bytesPerLine, QImage.Format_RGB888)
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.error_label.setText(f"Czas: {elapsed_time:.2f}s")
        self.reload_image()

    def apply_median_filter(self, image_channel):
        height, width = image_channel.shape
        half_size = 1
        filtered_image = np.zeros_like(image_channel)

        for i in range(half_size, height - half_size):
            for j in range(half_size, width - half_size):
                window = image_channel[i - half_size:i + half_size + 1, j - half_size:j + half_size + 1]
                median_value = np.median(window)
                filtered_image[i, j] = median_value

        return filtered_image




    def edge_detection(self):
        self.error_label.setText("Wykonywana funkcja: Sobel Edge Detection")
        start_time = time.time()
        img_data = np.array(self.image)
        img_data = img_data.astype(np.int32)

        # Przygotowanie kerneli Sobela
        sobel_x = np.array([[-1, 0, 1],
                            [-2, 0, 2],
                            [-1, 0, 1]])

        sobel_y = np.array([[-1, -2, -1],
                            [0, 0, 0],
                            [1, 2, 1]])

        # Inicjalizacja obrazu wynikowego
        edge_img_data = np.zeros_like(img_data)

        for c in range(3):
            channel = img_data[:, :, c]
            gradient_x = convolve2d(channel, sobel_x, mode='same', boundary='wrap')
            gradient_y = convolve2d(channel, sobel_y, mode='same', boundary='wrap')

            # Obliczenie kierunku gradientu i magnitude
            gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)

            # Normalizacja magnitude do zakresu [0, 255]
            gradient_magnitude = (gradient_magnitude / np.max(gradient_magnitude)) * 255

            edge_img_data[:, :, c] = gradient_magnitude

        img_data = np.clip(edge_img_data, 0, 255).astype(np.uint8)
        self.image = img_data

        height, width, channel = img_data.shape
        bytesPerLine = 3 * width
        self.q_image = QImage(img_data.data, width, height, bytesPerLine, QImage.Format_RGB888)
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.error_label.setText(f"Czas: {elapsed_time:.2f}s")
        self.reload_image()


    def high_pass(self):
        self.error_label.setText("Wykonywana funkcja: high-pass (filtr wyostrzający)")
        start_time = time.time()
        img_data = np.array(self.image)
        img_data = img_data.astype(np.int32)

        # Tworzenie kernela filtru wyostrzającego
        kernel = np.array([[-1, -1, -1],
                           [-1, 9, -1],
                           [-1, -1, -1]])

        # Zastosowanie filtru wyostrzającego na każdym kanale koloru
        sharpened_img_data = np.zeros_like(img_data)
        for c in range(3):
            channel = img_data[:, :, c]
            sharpened_channel = sharpened_img_data[:, :, c]

            sharpened_channel[1:-1, 1:-1] = convolve2d(channel, kernel, mode='valid')

        img_data = np.clip(sharpened_img_data, 0, 255).astype(np.uint8)
        self.image = img_data

        height, width, channel = img_data.shape
        bytesPerLine = 3 * width
        self.q_image = QImage(img_data.data, width, height, bytesPerLine, QImage.Format_RGB888)
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.error_label.setText(f"Czas: {elapsed_time:.2f}s")
        self.reload_image()


    def gaussian_blur(self):
        self.error_label.setText("Wykonywana funkcja: gaussian_blur (rozmycie gaussowskie)")
        start_time = time.time()
        img_data = np.array(self.image)
        img_data = img_data.astype(np.int32)

        # Tworzenie kernela rozmycia gaussowskiego
        kernel = np.array([[1, 2, 1],
                           [2, 4, 2],
                           [1, 2, 1]]) / 16

        # Zastosowanie rozmycia gaussowskiego na każdym kanale koloru
        blurred_img_data = np.zeros_like(img_data)
        for c in range(3):
            channel = img_data[:, :, c]
            blurred_channel = blurred_img_data[:, :, c]

            blurred_channel[1:-1, 1:-1] = convolve2d(channel, kernel, mode='valid')

        img_data = np.clip(blurred_img_data, 0, 255).astype(np.uint8)
        self.image = img_data

        height, width, channel = img_data.shape
        bytesPerLine = 3 * width
        self.q_image = QImage(img_data.data, width, height, bytesPerLine, QImage.Format_RGB888)
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.error_label.setText(f"Czas: {elapsed_time:.2f}s")
        self.reload_image()


    def mask_veave(self):
        print("mask veave")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())


# def smoothing(self):
    #     self.error_label.setText("Wykonywana funkcja: smoothing")
    #     start_time = time.time()

    #     image_data = np.array(self.image)
    #     filter_size = 3
    #     half_size = filter_size // 2
    #     img_height, img_width, _ = image_data.shape

    #     smoothed_image = np.zeros_like(image_data, dtype=np.uint8)

    #     for y in range(half_size, img_height - half_size):
    #         for x in range(half_size, img_width - half_size):
    #             window = image_data[y - half_size:y + half_size + 1, x - half_size:x + half_size + 1, :]
    #             r_avg = np.mean(window[:, :, 0])
    #             g_avg = np.mean(window[:, :, 1])
    #             b_avg = np.mean(window[:, :, 2])

    #             smoothed_image[y, x, 0] = r_avg
    #             smoothed_image[y, x, 1] = g_avg
    #             smoothed_image[y, x, 2] = b_avg

    #     self.image = smoothed_image

    #     height, width, channel = smoothed_image.shape
    #     bytesPerLine = 3 * width
    #     self.q_image = QImage(smoothed_image.data, width, height, bytesPerLine, QImage.Format_RGB888)

    #     end_time = time.time()
    #     elapsed_time = end_time - start_time
    #     self.error_label.setText(f"Czas: {elapsed_time:.2f}s")

    #     self.reload_image()


    # def median(self):
    #     # Ustaw komunikat na etykiecie przed rozpoczęciem przetwarzania
    #     self.error_label.setText("Wykonywana funkcja: median")

    #     # Rozpocznij pomiar czasu
    #     start_time = time.time()

    #     # Stworzenie kopii obrazu, aby nie modyfikować oryginalnego
    #     median_image = np.array(self.image)

    #     # Definicja rozmiaru filtra
    #     filter_size = 3  # Możesz dostosować rozmiar filtra według potrzeb

    #     # Obliczenie połowy rozmiaru filtra
    #     half_size = filter_size // 2

    #     # Kopiowanie obrazu do zmiennej pomocniczej
    #     img_data = np.array(self.image)

    #     # Iteracja przez piksele obrazu
    #     for y in range(half_size, img_data.shape[0] - half_size):
    #         for x in range(half_size, img_data.shape[1] - half_size):
    #             # Inicjalizacja listy kanałów RGB
    #             r_values, g_values, b_values = [], [], []

    #             # Iteracja przez otoczenie piksela
    #             for i in range(-half_size, half_size + 1):
    #                 for j in range(-half_size, half_size + 1):
    #                     # Dodawanie kolorów piksela do list
    #                     r_values.append(img_data[y + i, x + j, 0])
    #                     g_values.append(img_data[y + i, x + j, 1])
    #                     b_values.append(img_data[y + i, x + j, 2])

    #             # Obliczenie mediany dla każdego kanału RGB
    #             r_median = np.median(r_values)
    #             g_median = np.median(g_values)
    #             b_median = np.median(b_values)

    #             # Ustawienie nowych wartości piksela w obrazie z filtrem medianowym
    #             median_image[y, x, 0] = r_median
    #             median_image[y, x, 1] = g_median
    #             median_image[y, x, 2] = b_median

    #     # Przypisanie obrazu z filtrem medianowym do self.image
    #     self.image = median_image

    #     # Konwersja obrazu z NumPy array z powrotem na QImage
    #     height, width, channel = median_image.shape
    #     bytesPerLine = 3 * width
    #     self.q_image = QImage(median_image.data, width, height, bytesPerLine, QImage.Format_RGB888)

    #     # Zakończ pomiar czasu
    #     end_time = time.time()
    #     elapsed_time = end_time - start_time

    #     # Ustaw komunikat z czasem na etykiecie
    #     self.error_label.setText(f"Poprawnie wykonano funkcję. Czas wykonania: {elapsed_time:.2f} sekund")

    #     # Odświeżenie wyświetlanego obrazu
    #     self.reload_image()
