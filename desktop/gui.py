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
        ber_input = QLineEdit()  # Create a new QLineEdit for BER
        self.param_inputs['BER'] = ber_input  # Store it
        self.param_form.addRow("BER:", ber_input)

    def update_input_fields(self):
        """Update input fields based on the selected channel."""
        # Clear all existing rows
        while self.param_form.rowCount() > 0:
            self.param_form.removeRow(0)

        # Add appropriate input fields
        if self.channel_select.currentText() == 'BSC':
            ber_input = QLineEdit()  # Create a new QLineEdit for BER
            self.param_inputs['BER'] = ber_input  # Store it
            self.param_form.addRow("Bit Error Rate (BER):", ber_input)
        else:  # Gilbert-Elliott
            self.param_inputs['chance_for_bad'] = QLineEdit()
            self.param_inputs['chance_for_good'] = QLineEdit()
            self.param_inputs['p_err_good'] = QLineEdit()
            self.param_inputs['p_err_bad'] = QLineEdit()

            # Add input fields with descriptive labels
            self.param_form.addRow("Chance for Bad State (p):", self.param_inputs['chance_for_bad'])
            self.param_form.addRow("Chance for Good State (r):", self.param_inputs['chance_for_good'])
            self.param_form.addRow("Error Probability in Good State (1-k):", self.param_inputs['p_err_good'])
            self.param_form.addRow("Error Probability in Bad State (1-h):", self.param_inputs['p_err_bad'])

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

        if channel_model == 1:  # BSC
            try:
                ber = float(self.param_inputs['BER'].text())
                channel_params = ber
            except ValueError:
                print("Invalid BER value!")
                return
        else:  # Gilbert-Elliott
            try:
                params = [
                    float(self.param_inputs['chance_for_bad'].text()),  # p
                    float(self.param_inputs['chance_for_good'].text()),  # r
                    float(self.param_inputs['p_err_good'].text()),  # 1-k
                    float(self.param_inputs['p_err_bad'].text())  # 1-h
                ]
                channel_params = tuple(params)
            except ValueError:
                print("Invalid Gilbert-Elliott parameters!")
                return

        original_bits = self.image_to_bits(self.input_image)
        original_bit_count = original_bits.size

        if coding_type == 1:
            encoded_data = Hamming.CodeDataHammingObraz(original_bits)
        else:
            encoded_data = ConvolutionalCoder.CodeData(slowo=original_bits, JestObrazem=True)

        if channel_model == 1:  # BSC
            if coding_type == 1:
                transmitted_data, _, _ = bsc_channel_transmission_hamming(encoded_data, channel_params)
            else:
                transmitted_data, _, _ = bsc_channel_transmission_splot(encoded_data, channel_params)
        else:  # Gilbert-Elliott
            channel = GilbertElliottChannel(*channel_params)
            if coding_type == 1:
                transmitted_data = channel.transmitHamming(encoded_data)
            else:
                transmitted_data = channel.transmitConvolutional(encoded_data)

        noisy_non_decoded_bits = np.array(transmitted_data).flatten()[:original_bit_count]
        noisy_non_decoded_image = self.bits_to_image(noisy_non_decoded_bits, self.input_image.shape)
        self.display_image(noisy_non_decoded_image, self.noisy_image_label)

        if coding_type == 1:
            decoded_bits = Hamming.DecodeInputDataHammingObraz(transmitted_data)
        else:
            decoded_bits = ConvolutionalCoder.Decode(transmitted_data, tb_depth=3, czySlowo=False, JestObrazem=True)

        decoded_bits = np.array(decoded_bits).flatten()[:original_bit_count]
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
