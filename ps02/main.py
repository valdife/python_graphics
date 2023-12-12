import time
from PIL import Image
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QSlider, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSplitter, QScrollArea, QTextEdit, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
import sys
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QTextEdit, QPushButton, QSlider, QFileDialog, QSplitter
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from PIL import Image
header = {}
pixels = []

# * Wrapper to calculate function run time


def timeme(method):
    def wrapper(*args, **kw):
        startTime = time.time()
        result = method(*args, **kw)
        endTime = time.time()
        file_path = args[0]

        execution_time = endTime - startTime
        print(
            f"{method.__name__} took {execution_time:.6f} seconds for file {file_path}\n")
        return result

    return wrapper

# * Function to read header from file


def load_header(f):
    global pixel
    values = []
    read_lines = 0
    header = {
        'magic_number': None,
        'width': None,
        'height': None,
        'max_color_value': None
    }
    try:
        for line in f:
            read_lines += 1
            line = line.decode('latin-1').strip()
            words = line.split()
            for word in words:
                if word == "#" or word.startswith('#'):
                    break
                values.append(word)

            if len(values) >= 4:
                break

    except Exception as e:
        print(f"Error: {e}")
        return None
    header['magic_number'] = values[0]
    header['width'] = int(values[1])
    header['height'] = int(values[2])
    header['max_color_value'] = int(values[3])
    for value in values[4:]:
        try:
            pixels.append(int(value))
        except ValueError:

            # Function to load PPM image
            def load_ppm_image(file_path):
                with open(file_path, 'rb') as f:
                    header, read_lines = load_header(f)
                    if header['magic_number'] != 'P3' and header['magic_number'] != 'P6':
                        raise Exception("Invalid magic number")
                    if header['magic_number'] == 'P3':
                        print(f'Loading P3 file {file_path}')
                        file_content = f.read().decode('latin-1')
                        lines = file_content.split('\n')
                        new_pixels = [int(word) for line in lines for word in line.split() if word and not word.startswith("#") and word.isdigit()]
                        pixels = pixels + new_pixels
                    elif header['magic_number'] == 'P6':
                        print(f'Loading P6 file {file_path}')
                        f.seek(read_lines)
                        for _ in range(read_lines-1):
                            f.readline()
                        pixel_values = list(f.read())
                        pixels.extend(pixel_values)
                if len(pixels) != header['width'] * header['height'] * 3:
                    raise Exception(f"Invalid pixel count.\nExpected {header['width'] * header['height'] * 3} pixels\nLoaded {len(pixels)} pixels")
                else:
                    print(f'Pixels for {file_path} successfully loaded.\n{len(pixels)} pixels loaded.')

            # Function to load JPEG image
            def load_jpeg_image(file_path):
                try:
                    print(f'Loading JPEG file {file_path}')
                    im = Image.open(file_path)
                    if im.mode != 'RGB':
                        im = im.convert('RGB')
                    header['width'], header['height'] = im.size
                    header['max_color_value'] = 255
                    pixels.clear()
                    pixels.extend(im.tobytes())
                    print(f'Pixels for {file_path} successfully loaded.\n{len(pixels)} pixels loaded.')
                except Exception as e:
                    print(f"Error loading JPEG file {file_path}: {e}")

            # Gui class
            class ImageDisplayWindow(QMainWindow):
                def __init__(self):
                    super().__init__()
                    self.initUI()
                    self.loaded = False

                def initUI(self):
                    self.scale_factor = 1.0
                    self.pan_start = None

                    central_widget = QWidget(self)
                    layout = QHBoxLayout(central_widget)

                    self.image_label = QLabel()
                    self.image_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

                    scroll_area = QScrollArea(self)
                    scroll_area.setWidgetResizable(True)
                    scroll_area.setWidget(self.image_label)
                    scroll_area.setMouseTracking(True)

                    right_menu = QWidget(self)
                    right_menu_layout = QVBoxLayout(right_menu)
                    right_menu_layout.setContentsMargins(20, 20, 20, 20)

                    self.text_edit = QTextEdit()
                    self.text_edit.setFixedWidth(150)
                    self.text_edit.setFixedHeight(26)

                    button_layout = QVBoxLayout()

                    zoom_in_button = QPushButton("Zoom In")
                    zoom_out_button = QPushButton("Zoom Out")
                    load_image_button = QPushButton("Load Image")

                    zoom_in_button.clicked.connect(self.zoomIn)
                    zoom_out_button.clicked.connect(self.zoomOut)
                    load_image_button.clicked.connect(self.loadImage)

                    button_layout.addWidget(zoom_in_button)
                    button_layout.addWidget(zoom_out_button)
                    button_layout.addWidget(load_image_button)

                    self.export_quality_text = QTextEdit()
                    self.export_quality_text.setFixedWidth(150)
                    self.export_quality_text.setFixedHeight(26)

                    quality_slider = QSlider(Qt.Horizontal)
                    quality_slider.setRange(0, 100)
                    quality_slider.setValue(90)
                    quality_slider.setTickInterval(10)
                    quality_slider.setTickPosition(QSlider.TicksAbove)
                    quality_slider.valueChanged.connect(self.updateExportQuality)

                    export_button = QPushButton("Export as JPEG")
                    export_button.clicked.connect(self.exportAsJPEG)

                    compression_layout = QVBoxLayout()
                    compression_layout.addWidget(self.export_quality_text)
                    compression_layout.addWidget(quality_slider)
                    compression_layout.addWidget(export_button)

                    right_menu_layout.addWidget(self.text_edit)
                    right_menu_layout.addLayout(button_layout)
                    right_menu_layout.addLayout(compression_layout)

                    right_menu.setStyleSheet("background-color: lightgray;")

                    splitter = QSplitter(Qt.Horizontal)
                    splitter.addWidget(scroll_area)
                    splitter.addWidget(right_menu)
                    splitter.setSizes([1920, 150])

                    layout.addWidget(splitter)

                    self.setCentralWidget(central_widget)
                    self.setGeometry(0, 0, 1920, QDesktopWidget().availableGeometry().height())
                    self.show()

                    self.image = None
                    self.export_quality = 90
                    self.export_quality_text.setPlainText(f"Quality: {self.export_quality}%")

                def linearScaling(self):
                    maxValue = max(pixels)
                    for i in range(len(pixels)):
                        pixels[i] = int(pixels[i] * (255/maxValue))

                def updateExportQuality(self, value):
                    self.export_quality = value
                    self.export_quality_text.setPlainText(f"Quality: {self.export_quality}%")

                def exportAsJPEG(self):
                    if self.image is not None:
                        options = QFileDialog.Options()
                        file_path, _ = QFileDialog.getSaveFileName(self, "Save as JPEG", "", "JPEG Files (*.jpg *.jpeg);;All Files (*)", options=options)
                        if file_path:
                            self.image.save(file_path, quality=self.export_quality)

                def createImage(self):
                    width = header['width']
                    height = header['height']
                    format = QImage.Format_RGB888
                    self.image = QImage(bytes(pixels), width, height, width * 3, format)

                def updateImage(self):
                    if self.image:
                        if not self.loaded:
                            scroll_area = self.image_label.parentWidget()
                            available_width = scroll_area.width()
                            available_height = scroll_area.height()
                            width_scale = available_width / self.image.width()
                            height_scale = available_height / self.image.height()
                            self.scale_factor = min(width_scale, height_scale)
                        scaled_image = self.image.scaled(int(self.image.width() * self.scale_factor), int(self.image.height() * self.scale_factor), Qt.KeepAspectRatio)
                        pixmap = QPixmap.fromImage(scaled_image)
                        self.image_label.setPixmap(pixmap)

                def zoomIn(self):
                    if hasattr(self, 'image') and self.image:
                        self.scale_factor *= 1.1
                        self.updateImage()

                def zoomOut(self):
                    if hasattr(self, 'image') and self.image:
                        self.scale_factor /= 1.1
                        self.updateImage()

                def mousePressEvent(self, event):
                    if event.button() == Qt.LeftButton:
                        self.pan_start = event.pos()

                def mouseMoveEvent(self, event):
                    if hasattr(self, 'image') and self.image:
                        if self.pan_start:
                            delta = self.pan_start - event.pos()
                            splitter = self.centralWidget().layout().itemAt(0).widget()
                            scroll_area = splitter.widget(0)
                            scroll_area.horizontalScrollBar().setValue(scroll_area.horizontalScrollBar().value() + delta.x())
                            scroll_area.verticalScrollBar().setValue(scroll_area.verticalScrollBar().value() + delta.y())
                            self.pan_start = event.pos()
                        image_pos = self.image_label.mapFrom(self, event.pos())
                        x = image_pos.x()
                        y = image_pos.y()
                        original_x = int(x / self.scale_factor)
                        original_y = int(y / self.scale_factor)
                        if 0 <= original_x < header['width'] and 0 <= original_y < header['height']:
                            index = (original_y * header['width'] + original_x) * 3
                            r, g, b = pixels[index], pixels[index + 1], pixels[index + 2]
                            self.text_edit.setPlainText(f"RGB: ({r}, {g}, {b})")
                        else:
                            self.text_edit.setPlainText("RGB: (N/A)")

                def mouseReleaseEvent(self, event):
                    if event.button() == Qt.LeftButton:
                        self.pan_start = None

                def loadImage(self):
                    self.loaded = False
                    options = QFileDialog.Options()
                    options |= QFileDialog.ReadOnly
                    file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Image Files (*.ppm *.jpeg *.jpg);;All Files (*)", options=options)
                    if file_path:
                        global header, pixels
                        header = {}
                        pixels = []

                        if file_path.endswith('.ppm'):
                            load_ppm_image(file_path)
                        elif file_path.endswith(('.jpeg', '.jpg')):
                            load_jpeg_image(file_path)
                        else:
                            print("Unsupported image format")
                        if header['max_color_value'] > 255:
                            self.linearScaling()
                        self.createImage()
                        self.updateImage()
                        self.loaded = True


            if __name__ == "__main__":
                app = QApplication(sys.argv)
                window = ImageDisplayWindow()
                window.showMaximized()
                sys.exit(app.exec_())
