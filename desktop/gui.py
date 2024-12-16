import sys
import numpy as np
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                               QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QFileDialog, QLineEdit)
from PySide6.QtGui import QPixmap, QImage, QWheelEvent, QMouseEvent, QPainter
from PySide6.QtCore import Qt, QPoint
from PIL import Image
from Utils.BSC import *
from Utils.GilbertElliot import *
from Utils.Hamming import *
from Utils.HelperFunctions import *
from Utils.Convolutional import *

class ZoomableLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self._pixmap = None
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)  # Offset for dragging
        self.last_mouse_position = None

    def set_pixmap(self, pixmap):
        """Set the pixmap to display and reset scale."""
        self._pixmap = pixmap
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.update_pixmap()

    def wheelEvent(self, event: QWheelEvent):
        """Zoom in or out based on mouse wheel movement."""
        if event.angleDelta().y() > 0:
            self.scale_factor *= 1.1  # Zoom in
        else:
            self.scale_factor *= 0.9  # Zoom out
        self.update_pixmap()

    def mousePressEvent(self, event: QMouseEvent):
        """Start dragging on mouse press."""
        if event.button() == Qt.LeftButton:
            self.last_mouse_position = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle dragging to move the image."""
        if self.last_mouse_position is not None:
            delta = event.pos() - self.last_mouse_position
            self.offset += delta
            self.last_mouse_position = event.pos()
            self.update_pixmap()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """End dragging on mouse release."""
        if event.button() == Qt.LeftButton:
            self.last_mouse_position = None

    def update_pixmap(self):
        """Scale and update the displayed pixmap with offset."""
        if self._pixmap:
            scaled_pixmap = self._pixmap.scaled(self._pixmap.size() * self.scale_factor,
                                                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            result_pixmap = QPixmap(scaled_pixmap.size())
            result_pixmap.fill(Qt.transparent)

            painter_offset_x = self.offset.x()
            painter_offset_y = self.offset.y()
            painter = QPainter(result_pixmap)
            painter.drawPixmap(painter_offset_x, painter_offset_y, scaled_pixmap)
            painter.end()

            self.setPixmap(result_pixmap)


class TransmissionSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        width_20 = int(screen_width * 0.2)
        height_40 = int(screen_height * 0.4)

        self.setWindowTitle('Data Transmission Simulator')
        self.setGeometry(200, 100, int(screen_width * 0.7), int(screen_height * 0.8))

        main_layout = QHBoxLayout()
        image_grid = QGridLayout()

        # Create ZoomableLabels for images
        self.input_image_label = ZoomableLabel()
        self.noisy_image_label = ZoomableLabel()
        self.decoded_image_label = ZoomableLabel()
        self.additional_image_label = ZoomableLabel()

        for label in [self.input_image_label, self.noisy_image_label, self.decoded_image_label, self.additional_image_label]:
            label.setFixedSize(width_20, height_40)
            label.setStyleSheet("border: 1px solid black;")

        image_grid.addWidget(self.input_image_label, 0, 0)
        image_grid.addWidget(self.noisy_image_label, 0, 1)
        image_grid.addWidget(self.decoded_image_label, 1, 0)
        image_grid.addWidget(self.additional_image_label, 1, 1)
        main_layout.addLayout(image_grid)

        # Control panel with nested layouts
        control_layout = QVBoxLayout()
        select_layout = QHBoxLayout()

        self.channel_select = QComboBox()
        self.channel_select.addItems(['BSC', 'Gilbert-Elliott'])
        self.channel_select.currentIndexChanged.connect(self.update_input_fields)
        self.coding_select = QComboBox()
        self.coding_select.addItems(['Hamming', 'Convolutional'])

        select_layout.addWidget(QLabel("Select Coding Type"))
        select_layout.addWidget(self.coding_select)
        select_layout.addWidget(QLabel("Select Channel"))
        select_layout.addWidget(self.channel_select)
        control_layout.addLayout(select_layout)

        # Input fields for BER and Gilbert-Elliott params
        self.param_form = QFormLayout()
        self.param_inputs = {}
        self.create_input_fields()
        control_layout.addLayout(self.param_form)

        self.load_btn = QPushButton('Load Image')
        self.load_btn.clicked.connect(self.load_image)
        control_layout.addWidget(self.load_btn)

        self.transmit_btn = QPushButton('Transmit & Decode')
        self.transmit_btn.clicked.connect(self.transmit_and_decode)
        control_layout.addWidget(self.transmit_btn)

        main_layout.addLayout(control_layout)
        self.setLayout(main_layout)

    def create_input_fields(self):
        """Initialize input fields for BER and Gilbert-Elliott parameters."""
        self.param_inputs = {}  # Clear existing inputs
        for name in ['BER', 'p_bad', 'p_good', 'e_good', 'e_bad']:
            input_field = QLineEdit()
            self.param_inputs[name] = input_field

    def update_input_fields(self):
        """Update input fields based on the selected channel."""
        # Clear all existing rows
        while self.param_form.rowCount() > 0:
            self.param_form.removeRow(0)

        # Add appropriate input fields
        if self.channel_select.currentText() == 'BSC':
            ber_input = QLineEdit()  # Create a new QLineEdit for BER
            self.param_inputs['BER'] = ber_input  # Store it
            self.param_form.addRow("BER:", ber_input)
        else:  # Gilbert-Elliott
            for param in ['p_bad', 'p_good', 'e_good', 'e_bad']:
                param_input = QLineEdit()  # Create a new QLineEdit for each parameter
                self.param_inputs[param] = param_input  # Store it
                self.param_form.addRow(f"{param}:", param_input)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open Image File', '', 'BMP Files (*.bmp)')
        if file_path:
            self.input_image = self.load_bmp_image(file_path)
            self.display_image(self.input_image, self.input_image_label)

    def load_bmp_image(self, file_path):
        image = Image.open(file_path).convert('RGB')
        return np.array(image)

    def display_image(self, image_array, label):
        height, width, _ = image_array.shape
        qimage = QImage(image_array.data, width, height, 3 * width, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        label.set_pixmap(pixmap)


    def transmit_and_decode(self):
        """Simulate transmission with FEC correction."""
        coding_type = 1 if self.coding_select.currentText() == 'Hamming' else 2
        channel_model = 1 if self.channel_select.currentText() == 'BSC' else 2

        # Retrieve parameters from input fields
        if channel_model == 1:  # BSC
            try:
                ber = float(self.param_inputs['BER'].text())
                channel_params = ber
            except ValueError:
                print("Invalid BER value!")
                return
        else:  # Gilbert-Elliott
            try:
                params = [float(self.param_inputs[param].text()) for param in ['p_bad', 'p_good', 'e_good', 'e_bad']]
                channel_params = tuple(params)
            except ValueError:
                print("Invalid Gilbert-Elliott parameters!")
                return

        # Step 1: Encode the input image into bits
        original_bits = self.image_to_bits(self.input_image)
        original_bit_count = original_bits.size  # Track the original number of bits

        # Encode using the selected FEC method
        if coding_type == 1:
            encoded_data = Hamming.CodeDataHammingObraz(original_bits)
        else:
            encoded_data = ConvolutionalCoder.CodeData(slowo=original_bits, JestObrazem=True)

        # Step 2: Transmit through the selected channel
        if channel_model == 1:
            noisy_data, _ = bsc_channel_transmission_hamming(encoded_data, channel_params)
        else:
            channel = GilbertElliottChannel(*channel_params)
            noisy_data = channel.transmitHamming(encoded_data)

        noisy_non_decoded_bits = np.array(noisy_data).flatten()[:original_bit_count]
        noisy_non_decoded_image = self.bits_to_image(noisy_non_decoded_bits, self.input_image.shape)
        self.display_image(noisy_non_decoded_image, self.noisy_image_label)

        # Step 3: Decode the received data using the selected FEC method
        if coding_type == 1:
            decoded_bits = Hamming.DecodeInputDataHammingObraz(noisy_data)
        else:
            decoded_bits = ConvolutionalCoder.Decode(noisy_data, tb_depth=3, czySlowo=False, JestObrazem=True)

        # Ensure decoded bits are trimmed to the original size
        decoded_bits = np.array(decoded_bits).flatten()[:original_bit_count]

        # Convert the decoded bits back to an image
        decoded_image = self.bits_to_image(decoded_bits, self.input_image.shape)
        self.display_image(decoded_image, self.decoded_image_label)
        overlay_image = self.generate_overlay_image(self.input_image, decoded_image)
        self.display_image(overlay_image, self.additional_image_label)

    def image_to_bits(self, image):
        """Convert image data to a bit array."""
        return np.unpackbits(image)

    def bits_to_image(self, bits, shape):
        """Convert bit array back to image data."""
        return np.packbits(bits).reshape(shape)

    def generate_overlay_image(self, input_image, output_image):
        """Overlay two images to highlight differences."""
        diff = np.abs(input_image - output_image)
        return diff.astype(np.uint8)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    simulator = TransmissionSimulator()
    simulator.show()
    sys.exit(app.exec())
