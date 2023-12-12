import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
import cv2
import pyqtgraph as pg


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

        load_image_button = QPushButton("Load Image")
        load_image_button.clicked.connect(self.load_image)
        menu_layout.addWidget(load_image_button, 0, 0)

        refresh_image_button = QPushButton("Refresh Image")
        refresh_image_button.clicked.connect(self.reload_image_fresh)
        menu_layout.addWidget(refresh_image_button, 1, 0)

        show_histogram_button = QPushButton("Show Histogram")
        show_histogram_button.clicked.connect(self.show_histogram)
        menu_layout.addWidget(show_histogram_button, 2, 0)

        stretch_histogram_button = QPushButton("Stretch Histogram")
        stretch_histogram_button.clicked.connect(self.stretch_histogram)
        menu_layout.addWidget(stretch_histogram_button, 3, 0)

        equalize_histogram_button = QPushButton("Equalize Histogram")
        equalize_histogram_button.clicked.connect(self.equalize_histogram)
        menu_layout.addWidget(equalize_histogram_button, 4, 0)

        self.treshold_text = QLineEdit()
        self.treshold_text.setFixedHeight(30)
        self.treshold_text.setStyleSheet(
            "border-color: black; border-width: 2px; border-style: solid; border-radius:5px"
        )
        self.treshold_text.setValidator(QIntValidator(self))
        self.treshold_text.setText("0")
        menu_layout.addWidget(self.treshold_text, 5, 0)

        manual_treshold_button = QPushButton("Manual Threshold")
        manual_treshold_button.clicked.connect(self.manual_threshold)
        menu_layout.addWidget(manual_treshold_button, 6, 0)

        ptile_treshold_button = QPushButton("P-Tile Threshold")
        ptile_treshold_button.clicked.connect(self.ptile_threshold)
        menu_layout.addWidget(ptile_treshold_button, 7, 0)

        mean_iterative_button = QPushButton("Mean Iterative")
        mean_iterative_button.clicked.connect(self.mean_iterative)
        menu_layout.addWidget(mean_iterative_button, 8, 0)

        self.error_label = QLabel("No errors found")
        self.error_label.setFixedHeight(50)
        menu_layout.addWidget(self.error_label, 20, 0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.menu_container)
        splitter.addWidget(self.image_label)
        splitter.setSizes([200, 1920])

        layout.addWidget(splitter)

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
            file_path = "51119dark.jpg"
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
                self.image = cv2.resize(self.image, (new_width, new_height))
                bytesPerLine = 3 * new_width
                self.q_image = QImage(
                    self.image.data,
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
        pixmap = QPixmap.fromImage(self.q_image)
        self.image_label.setPixmap(pixmap)
        self.image = self.q_image

    def show_histogram(self):
        if hasattr(self, "image"):
            self.histogram_plot = pg.PlotWidget(self)
            self.histogram_plot.setFixedHeight(200)
            if isinstance(self.image, np.ndarray):
                if len(self.image.shape) == 3:
                    gray_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
                else:
                    gray_image = self.image
            elif isinstance(self.image, QImage):
                width = self.image.width()
                height = self.image.height()
                buffer = self.image.bits().asstring(width * height)
                gray_image = np.frombuffer(buffer, dtype=np.uint8).reshape(
                    (height, width)
                )
            hist, bins = np.histogram(gray_image, bins=256, range=(0, 256))
            hist_plot = self.histogram_plot.plot(
                bins, hist, stepMode=True, fillLevel=0, brush=(0, 0, 255, 150)
            )
            self.histogram_plot.setTitle("Histogram of the Loaded Image")
            self.histogram_plot.setLabel("left", "Frequency")
            self.histogram_plot.setLabel("bottom", "Pixel Value")
            dialog = QDialog(self)
            dialog.setWindowTitle("Histogram")
            dialog_width = 355
            dialog_height = 200
            dialog.setFixedSize(dialog_width, dialog_height)
            layout = QVBoxLayout()
            layout.addWidget(self.histogram_plot)
            dialog.setLayout(layout)
            dialog.exec_()
        else:
            print("No image loaded.")

    def stretch_histogram(self):
        if hasattr(self, "image"):
            r, g, b = cv2.split(self.image)
            r_nonzero_indices = np.where(r > 0)
            g_nonzero_indices = np.where(g > 0)
            b_nonzero_indices = np.where(b > 0)
            r_min_index = np.min(r[r_nonzero_indices])
            g_min_index = np.min(g[g_nonzero_indices])
            b_min_index = np.min(b[b_nonzero_indices])
            r_max_index = np.max(r[r_nonzero_indices])
            g_max_index = np.max(g[g_nonzero_indices])
            b_max_index = np.max(b[b_nonzero_indices])
            r_normalized = ((r - r_min_index) / (r_max_index - r_min_index)) * 255
            g_normalized = ((g - g_min_index) / (g_max_index - g_min_index)) * 255
            b_normalized = ((b - b_min_index) / (b_max_index - b_min_index)) * 255
            r_normalized = np.round(r_normalized).astype(np.uint8)
            g_normalized = np.round(g_normalized).astype(np.uint8)
            b_normalized = np.round(b_normalized).astype(np.uint8)
            equalized_image = cv2.merge((r_normalized, g_normalized, b_normalized))
            self.image = equalized_image
            self.q_image = QImage(
                equalized_image.data,
                equalized_image.shape[1],
                equalized_image.shape[0],
                equalized_image.strides[0],
                QImage.Format_RGB888,
            )
            self.reload_image()

    def equalize_histogram(self):
        if hasattr(self, "image"):
            r, g, b = cv2.split(self.image)

            def equalize_channel(channel):
                hist, bins = np.histogram(channel, bins=256, range=(0, 256))
                cdf = np.cumsum(hist)
                cdf_min = np.min(cdf)
                num_pixels = channel.size
                scale_factor = 255 / (num_pixels - cdf_min)
                equalized_channel = np.round(
                    (cdf[channel] - cdf_min) * scale_factor
                ).astype(np.uint8)
                return equalized_channel

            r_equalized = equalize_channel(r)
            g_equalized = equalize_channel(g)
            b_equalized = equalize_channel(b)
            equalized_image = cv2.merge((r_equalized, g_equalized, b_equalized))
            self.q_image = QImage(
                equalized_image.data,
                equalized_image.shape[1],
                equalized_image.shape[0],
                equalized_image.strides[0],
                QImage.Format_RGB888,
            )
            self.reload_image()
        else:
            print("No image loaded.")

    def manual_threshold(self):
        if hasattr(self, "image"):
            threshold_value = int(self.treshold_text.text())
            threshold_value = max(
                0, min(255, threshold_value)
            ) 

            if len(self.image.shape) == 3:
                gray_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
            else:
                gray_image = self.image

            binary_image = cv2.threshold(
                gray_image, threshold_value, 255, cv2.THRESH_BINARY
            )[1]

            self.q_image = QImage(
                binary_image.data,
                binary_image.shape[1],
                binary_image.shape[0],
                binary_image.strides[0],
                QImage.Format_Grayscale8,
            )
            self.reload_image()
        else:
            print("No image loaded.")

    def ptile_threshold(self, p):
        if hasattr(self, "image"):
            if len(self.image.shape) == 3:
                gray_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
            else:
                gray_image = self.image
            p = int(self.treshold_text.text())
            p = max(0, min(100, p))
            flattened_image = gray_image.flatten()
            flattened_image.sort()
            percentile_index = int((p / 100.0) * (len(flattened_image) - 1))
            threshold_value = flattened_image[percentile_index]
            _, binary_image = cv2.threshold(
                gray_image, threshold_value, 255, cv2.THRESH_BINARY
            )
            self.q_image = QImage(
                binary_image.data,
                binary_image.shape[1],
                binary_image.shape[0],
                binary_image.strides[0],
                QImage.Format_Grayscale8,
            )
            self.reload_image()
        else:
            print("No image loaded.")

    def mean_iterative(self):
        if hasattr(self, "image"):
            tolerance = int(self.treshold_text.text())
            if len(self.image.shape) == 3:
                gray_image = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
            else:
                gray_image = self.image
            threshold = np.mean(gray_image)
            while True:
                above_threshold = gray_image >= threshold
                below_threshold = gray_image < threshold
                mean_above = np.mean(gray_image[above_threshold])
                mean_below = np.mean(gray_image[below_threshold])
                new_threshold = 0.5 * (mean_above + mean_below)
                if abs(threshold - new_threshold) < tolerance:
                    break
                threshold = new_threshold
            _, binary_image = cv2.threshold(
                gray_image, threshold, 255, cv2.THRESH_BINARY
            )
            self.q_image = QImage(
                binary_image.data,
                binary_image.shape[1],
                binary_image.shape[0],
                binary_image.strides[0],
                QImage.Format_Grayscale8,
            )
            self.reload_image()
        else:
            print("No image loaded.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
