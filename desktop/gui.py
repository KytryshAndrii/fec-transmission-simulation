import sys
import numpy as np
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                               QVBoxLayout, QHBoxLayout, QComboBox, QFileDialog, QLineEdit)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt
from PIL import Image
from matplotlib.cbook import flatten

from Utils.BSC import *
from Utils.GilbertElliot import *
from Utils.Hamming import *
from Utils.HelperFunctions import *
from Utils.Convolutional import *


class TransmissionSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        width_70 = int(screen_width * 0.7)
        width_20 = int(screen_width * 0.2)
        height_80 = int(screen_height * 0.8)

        # Window title and size
        self.setWindowTitle('Data Transmission Simulator')
        self.setGeometry(200, 100, width_70, height_80)

        # Main layout: Horizontal split (left, center-left, center-right, right)
        main_layout = QHBoxLayout()

        # Left side (Input Image)
        self.input_image_label = QLabel()
        self.input_image_label.setFixedSize(width_20, height_80)
        self.input_image_label.setStyleSheet("border: 1px solid black;")
        main_layout.addWidget(self.input_image_label)

        # Center-left section (Noisy Image)
        self.noisy_image_label = QLabel()
        self.noisy_image_label.setFixedSize(width_20, height_80)
        self.noisy_image_label.setStyleSheet("border: 1px solid black;")
        main_layout.addWidget(self.noisy_image_label)

        # Center-right section (Decoded Image)
        self.decoded_image_label = QLabel()
        self.decoded_image_label.setFixedSize(width_20, height_80)
        self.decoded_image_label.setStyleSheet("border: 1px solid black;")
        main_layout.addWidget(self.decoded_image_label)

        # Right side (Controls)
        control_layout = QVBoxLayout()

        # Channel selection
        self.channel_select = QComboBox()
        self.channel_select.addItems(['BSC', 'Gilbert-Elliott'])
        self.channel_select.currentIndexChanged.connect(self.update_channel_parameters)
        control_layout.addWidget(QLabel("Select Channel"))
        control_layout.addWidget(self.channel_select)

        # Coding type selection
        self.coding_select = QComboBox()
        self.coding_select.addItems(['Hamming', 'Convolutional'])
        control_layout.addWidget(QLabel("Select Coding Type"))
        control_layout.addWidget(self.coding_select)

        # Channel parameters input
        self.param_input = QLineEdit()
        self.param_input.setPlaceholderText('Enter BER or Gilbert-Elliott params')
        control_layout.addWidget(QLabel("Set Channel Parameters"))
        control_layout.addWidget(self.param_input)

        # Load Image Button
        self.load_btn = QPushButton('Load Image')
        self.load_btn.clicked.connect(self.load_image)
        control_layout.addWidget(self.load_btn)

        # Transmit and decode button
        self.transmit_btn = QPushButton('Transmit & Decode')
        self.transmit_btn.clicked.connect(self.transmit_and_decode)
        control_layout.addWidget(self.transmit_btn)

        main_layout.addLayout(control_layout)
        self.setLayout(main_layout)

    def load_image(self):
        """Load an image file."""
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open Image File', '', 'BMP Files (*.bmp)')
        if file_path:
            self.input_image = self.load_bmp_image(file_path)
            self.display_image(self.input_image, self.input_image_label)

    def load_bmp_image(self, file_path):
        """Load an image and convert it to an RGB numpy array."""
        image = Image.open(file_path).convert('RGB')
        return np.array(image)

    def display_image(self, image_array, label):
        """Display a numpy image array on a QLabel."""
        height, width, _ = image_array.shape
        qimage = QImage(image_array.data, width, height, 3 * width, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio))

    def update_channel_parameters(self):
        """Update the input field placeholder based on selected channel."""
        if self.channel_select.currentText() == 'BSC':
            self.param_input.setPlaceholderText('Enter BER (e.g., 0.1)')
        else:
            self.param_input.setPlaceholderText('Enter Gilbert-Elliott params (p_bad, p_good, e_good, e_bad)')

    def transmit_and_decode(self):
        """Simulate transmission with FEC correction."""
        coding_type = 1 if self.coding_select.currentText() == 'Hamming' else 2
        channel_model = 1 if self.channel_select.currentText() == 'BSC' else 2

        params = self.param_input.text()
        if channel_model == 1:  # BSC
            ber = float(params)
            channel_params = ber
        else:  # Gilbert-Elliott
            try:
                params = [float(x) for x in params.split(',')]
                channel_params = tuple(params)
            except ValueError:
                print("Invalid Gilbert-Elliott parameters")
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

    def image_to_bits(self, image):
        """Convert image data to a bit array."""
        return np.unpackbits(image)

    def bits_to_image(self, bits, shape):
        """Convert bit array back to image data."""
        return np.packbits(bits).reshape(shape)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    simulator = TransmissionSimulator()
    simulator.show()
    sys.exit(app.exec())
