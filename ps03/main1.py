import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QSlider,
    QLineEdit,
    QRadioButton,
    QButtonGroup,
)
from PyQt5.QtCore import Qt, pyqtSignal

#* 0 for rgb to cmyk, 1 for cmyk to rgb
conv_type = "RGBtoCMYK"

# Define a function to convert CMYK values to RGB
def cmyk_to_rgb(c, m, y, k):
    r = 255 * (1 - c / 100) * (1 - k / 100)
    g = 255 * (1 - m / 100) * (1 - k / 100)
    b = 255 * (1 - y / 100) * (1 - k / 100)
    return int(r), int(g), int(b)

# Define a function to convert RGB values to CMYK
def rgb_to_cmyk(r, g, b):
    r = r / 255
    g = g / 255
    b = b / 255
    k = 1 - max(r, g, b)

    # Check if k is very close to 1 and set c, m, y to 0
    if abs(k - 1) < 1e-6:
        c, m, y = 0, 0, 0
    else:
        c = (1 - r - k) / (1 - k) * 100
        m = (1 - g - k) / (1 - k) * 100
        y = (1 - b - k) / (1 - k) * 100
    
    return int(c), int(m), int(y), int(k * 100)

# Define a class for the RGB color picker
class RGBColorPicker(QWidget):
    # Define a custom signal to emit RGB color values
    rgb_color_changed = pyqtSignal(int, int, int)

    def __init__(self):
        super().__init__()
        self.updating_labels = False

        # Initialize RGB values
        self.red = 0
        self.green = 0
        self.blue = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Create widgets for red, green, and blue
        self.red_label = QLabel("Red")
        self.red_slider = QSlider(Qt.Horizontal)
        self.red_slider.setRange(0, 255)

        self.green_label = QLabel("Green")
        self.green_slider = QSlider(Qt.Horizontal)
        self.green_slider.setRange(0, 255)

        self.blue_label = QLabel("Blue")
        self.blue_slider = QSlider(Qt.Horizontal)
        self.blue_slider.setRange(0, 255)

        self.red_input = QLineEdit()
        self.green_input = QLineEdit()
        self.blue_input = QLineEdit()

        self.color_label = QLabel()
        self.color_label.setAlignment(Qt.AlignCenter)

        # Add widgets to the layout
        layout.addWidget(self.red_label)
        layout.addWidget(self.red_slider)
        layout.addWidget(self.red_input)
        layout.addWidget(self.green_label)
        layout.addWidget(self.green_slider)
        layout.addWidget(self.green_input)
        layout.addWidget(self.blue_label)
        layout.addWidget(self.blue_slider)
        layout.addWidget(self.blue_input)
        layout.addWidget(self.color_label)

        self.setLayout(layout)

        # Connect slider value changes to update functions
        self.red_slider.valueChanged.connect(self.update_variables_from_slider)
        self.green_slider.valueChanged.connect(self.update_variables_from_slider)
        self.blue_slider.valueChanged.connect(self.update_variables_from_slider)

        # Connect text input changes to update functions
        self.red_input.textChanged.connect(self.update_variables_from_text)
        self.green_input.textChanged.connect(self.update_variables_from_text)
        self.blue_input.textChanged.connect(self.update_variables_from_text)
        self.update_labels()

    def update_variables_from_slider(self):
        if not self.updating_labels:
            # Update RGB values from sliders
            self.red = self.red_slider.value()
            self.green = self.green_slider.value()
            self.blue = self.blue_slider.value()

            # Emit the RGB color changed signal with updated values
            self.rgb_color_changed.emit(self.red, self.green, self.blue)
            self.update_labels()

    def update_variables_from_text(self):
        if not self.updating_labels:
            try:
                red_text = self.red_input.text()
                if red_text:
                    self.red = min(int(red_text), 255)  # Limit to a maximum of 255
                else:
                    self.red = 0  # Handle empty input
            except ValueError:
                pass

            try:
                green_text = self.green_input.text()
                if green_text:
                    self.green = min(int(green_text), 255)  # Limit to a maximum of 255
                else:
                    self.green = 0  # Handle empty input
            except ValueError:
                pass

            try:
                blue_text = self.blue_input.text()
                if blue_text:
                    self.blue = min(int(blue_text), 255)  # Limit to a maximum of 255
                else:
                    self.blue = 0  # Handle empty input
            except ValueError:
                pass

            # Emit the RGB color changed signal with updated values
            self.rgb_color_changed.emit(self.red, self.green, self.blue)
            self.update_labels()

    def update_labels(self):
        self.updating_labels = True
        # Update sliders and text inputs based on RGB values
        self.red_slider.setValue(self.red)
        self.green_slider.setValue(self.green)
        self.blue_slider.setValue(self.blue)
        self.red_input.setText(str(self.red))
        self.green_input.setText(str(self.green))
        self.blue_input.setText(str(self.blue))
        # Update color label background based on RGB values
        self.color_label.setStyleSheet(
            f"background-color: rgb({self.red}, {self.green}, {self.blue});"
        )
        self.updating_labels = False

    def update_color_from_cmyk(self, c, m, y, k):
        global conv_type
        if conv_type == "CMYKtoRGB":
            # Convert CMYK to RGB and update RGB values
            self.red, self.green, self.blue = cmyk_to_rgb(c, m, y, k)
            self.update_labels()

# Define a class for the CMYK color picker
class CMYKColorPicker(QWidget):
    # Define a custom signal to emit CMYK color values
    cmyk_color_changed = pyqtSignal(int, int, int, int)

    def __init__(self):
        super().__init__()
        self.updating_labels = False
        self.cyan = 0
        self.magenta = 0
        self.yellow = 0
        self.black = 100
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Create widgets for cyan, magenta, yellow, and black
        self.cyan_label = QLabel("Cyan")
        self.cyan_slider = QSlider(Qt.Horizontal)
        self.cyan_slider.setRange(0, 100)

        self.magenta_label = QLabel("Magenta")
        self.magenta_slider = QSlider(Qt.Horizontal)
        self.magenta_slider.setRange(0, 100)

        self.yellow_label = QLabel("Yellow")
        self.yellow_slider = QSlider(Qt.Horizontal)
        self.yellow_slider.setRange(0, 100)

        self.black_label = QLabel("Black")
        self.black_slider = QSlider(Qt.Horizontal)
        self.black_slider.setRange(0, 100)

        self.cyan_input = QLineEdit()
        self.magenta_input = QLineEdit()
        self.yellow_input = QLineEdit()
        self.black_input = QLineEdit()

        self.cmyk_color_label = QLabel()
        self.cmyk_color_label.setAlignment(Qt.AlignCenter)

        # Add widgets to the layout
        layout.addWidget(self.cyan_label)
        layout.addWidget(self.cyan_slider)
        layout.addWidget(self.cyan_input)
        layout.addWidget(self.magenta_label)
        layout.addWidget(self.magenta_slider)
        layout.addWidget(self.magenta_input)
        layout.addWidget(self.yellow_label)
        layout.addWidget(self.yellow_slider)
        layout.addWidget(self.yellow_input)
        layout.addWidget(self.black_label)
        layout.addWidget(self.black_slider)
        layout.addWidget(self.black_input)
        layout.addWidget(self.cmyk_color_label)

        self.setLayout(layout)

        # Connect slider value changes to update functions
        self.cyan_slider.valueChanged.connect(self.update_variables_from_slider)
        self.magenta_slider.valueChanged.connect(self.update_variables_from_slider)
        self.yellow_slider.valueChanged.connect(self.update_variables_from_slider)
        self.black_slider.valueChanged.connect(self.update_variables_from_slider)

        # Connect text input changes to update functions
        self.cyan_input.textChanged.connect(self.update_variables_from_text)
        self.magenta_input.textChanged.connect(self.update_variables_from_text)
        self.yellow_input.textChanged.connect(self.update_variables_from_text)
        self.black_input.textChanged.connect(self.update_variables_from_text)
        self.update_labels()

    def update_variables_from_slider(self):
        if not self.updating_labels:
            # Update CMYK values from sliders
            self.cyan = self.cyan_slider.value()
            self.magenta = self.magenta_slider.value()
            self.yellow = self.yellow_slider.value()
            self.black = self.black_slider.value()
            # Emit the CMYK color changed signal with updated values
            self.cmyk_color_changed.emit(
                self.cyan, self.magenta, self.yellow, self.black
            )
            self.update_labels()

    def update_variables_from_text(self):
        if not self.updating_labels:
            try:
                cyan_text = self.cyan_input.text()
                if cyan_text:
                    self.cyan = min(int(cyan_text), 100)  # Limit to a maximum of 100
                else:
                    self.cyan = 0  # Handle empty input
            except ValueError:
                pass

            try:
                magenta_text = self.magenta_input.text()
                if magenta_text:
                    self.magenta = min(
                        int(magenta_text), 100
                    )  # Limit to a maximum of 100
                else:
                    self.magenta = 0  # Handle empty input
            except ValueError:
                pass

            try:
                yellow_text = self.yellow_input.text()
                if yellow_text:
                    self.yellow = min(
                        int(yellow_text), 100
                    )  # Limit to a maximum of 100
                else:
                    self.yellow = 0  # Handle empty input
            except ValueError:
                pass

            try:
                black_text = self.black_input.text()
                if black_text:
                    self.black = min(int(black_text), 100)  # Limit to a maximum of 100
                else:
                    self.black = 0  # Handle empty input
            except ValueError:
                pass

            # Emit the CMYK color changed signal with updated values
            self.cmyk_color_changed.emit(
                self.cyan, self.magenta, self.yellow, self.black
            )
            self.update_labels()

    def update_labels(self):
        self.updating_labels = True
        # Update sliders and text inputs based on CMYK values
        self.cyan_slider.setValue(self.cyan)
        self.magenta_slider.setValue(self.magenta)
        self.yellow_slider.setValue(self.yellow)
        self.black_slider.setValue(self.black)
        self.cyan_input.setText(str(self.cyan))
        self.magenta_input.setText(str(self.magenta))
        self.yellow_input.setText(str(self.yellow))
        self.black_input.setText(str(self.black))
        r, g, b = cmyk_to_rgb(self.cyan, self.magenta, self.yellow, self.black)
        # Update color label background based on RGB values obtained from CMYK
        self.cmyk_color_label.setStyleSheet(f"background-color: rgb({r}, {g}, {b});")
        self.updating_labels = False

    def update_color_from_rgb(self, red, green, blue):
        global conv_type
        if conv_type == "RGBtoCMYK":
            # Convert RGB to CMYK and update CMYK values
            self.cyan, self.magenta, self.yellow, self.black = rgb_to_cmyk(
                red, green, blue
            )
            self.update_labels()

# Define the main application window
class ColorPickerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        rgb_color_picker = RGBColorPicker()
        cmyk_color_picker = CMYKColorPicker()

        main_layout = QVBoxLayout()

        # Create radio buttons for RGB to CMYK and CMYK to RGB conversion
        self.rgb_to_cmyk_radio = QRadioButton("RGB to CMYK")
        self.cmyk_to_rgb_radio = QRadioButton("CMYK to RGB")
        self.conversion_radio_group = QButtonGroup()
        self.conversion_radio_group.addButton(self.rgb_to_cmyk_radio)
        self.conversion_radio_group.addButton(self.cmyk_to_rgb_radio)
        main_layout.addWidget(self.rgb_to_cmyk_radio)
        main_layout.addWidget(self.cmyk_to_rgb_radio)
        main_layout.addWidget(rgb_color_picker)
        main_layout.addWidget(cmyk_color_picker)
        self.rgb_to_cmyk_radio.setChecked(True)
        self.rgb_to_cmyk_radio.toggled.connect(self.change_to_rgb)
        self.cmyk_to_rgb_radio.toggled.connect(self.change_to_cmyk)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Connect the RGB and CMYK color changed signals
        rgb_color_picker.rgb_color_changed.connect(
            cmyk_color_picker.update_color_from_rgb
        )
        cmyk_color_picker.cmyk_color_changed.connect(
            rgb_color_picker.update_color_from_cmyk
        )

        # Adjust the height to accommodate both RGB and CMYK sections
        self.setGeometry(100, 100, 400, 500)
        self.setWindowTitle("RGB and CMYK Color Picker")
        self.show()

    def change_to_rgb(self):
        global conv_type
        conv_type = "RGBtoCMYK"

    def change_to_cmyk(self):
        global conv_type
        conv_type = "CMYKtoRGB"

# Define the main function to run the application
def main():
    app = QApplication(sys.argv)
    ex = ColorPickerApp()
    sys.exit(app.exec_())

# Check if the script is being run directly and not imported as a module
if __name__ == "__main__":
    main()
