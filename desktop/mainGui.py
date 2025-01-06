import sys
import numpy as np
from PIL import Image
import multiprocessing as mp
from zoomable_label import ZoomableLabel
from PySide6.QtGui import QPixmap, QImage
from desktop.ImageProcessingFunctions import encode_data, image_to_bits, bits_to_image
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QComboBox, QFileDialog, QLineEdit, QFormLayout)
from ImageProcessingFunctions import split_image, transmit_bsc, transmit_gilbert_elliott, decode_image_part, merge_image

class TransmissionSimulator(QWidget):
    def __init__(self):
        super().__init__()
        self.transmit_btn = None
        self.load_btn = None
        self.param_inputs = None
        self.param_form = None
        self.coding_select = None
        self.channel_select = None
        self.additional_image_label = None
        self.decoded_image_label = None
        self.noisy_image_label = None
        self.input_image_label = None
        self.input_image = None
        self.initUI()

    def initUI(self):
        screen = QApplication.primaryScreen()
        if not screen:
            print("Error: Unable to detect primary screen. Exiting.")
            sys.exit(1)

        screen_size = screen.size()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        width_20 = int(screen_width * 0.2)
        height_40 = int(screen_height * 0.4)

        self.setWindowTitle('Data Transmission Simulator')
        self.setGeometry(200, 100, int(screen_width * 0.7), int(screen_height * 0.8))

        main_layout = QHBoxLayout()
        image_grid = QGridLayout()

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
        ber_input = QLineEdit()
        self.param_inputs['BER'] = ber_input
        self.param_form.addRow("BER:", ber_input)

    def update_input_fields(self):
        """Update input fields based on the selected channel."""
        while self.param_form.rowCount() > 0:
            self.param_form.removeRow(0)

        if self.channel_select.currentText() == 'BSC':
            ber_input = QLineEdit()
            self.param_inputs['BER'] = ber_input
            self.param_form.addRow("Bit Error Rate (BER):", ber_input)
        else:  # Gilbert-Elliott
            self.param_inputs['chance_for_bad'] = QLineEdit()
            self.param_inputs['chance_for_good'] = QLineEdit()
            self.param_inputs['p_err_good'] = QLineEdit()
            self.param_inputs['p_err_bad'] = QLineEdit()

            self.param_form.addRow("Chance for Bad State (p):", self.param_inputs['chance_for_bad'])
            self.param_form.addRow("Chance for Good State (r):", self.param_inputs['chance_for_good'])
            self.param_form.addRow("Error Probability in Good State (1-k):", self.param_inputs['p_err_good'])
            self.param_form.addRow("Error Probability in Bad State (1-h):", self.param_inputs['p_err_bad'])

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open Image File', '', 'BMP Files (*.bmp)')
        if not file_path:
            print("No file selected.")
            return

        try:
            self.input_image = self.load_bmp_image(file_path)
            self.display_image(self.input_image, self.input_image_label)
        except Exception as e:
            print(f"Error loading image: {e}")

    def load_bmp_image(self, file_path):
        image = Image.open(file_path).convert('RGB')
        return np.array(image)

    def display_image(self, image_array, label):
        try:
            height, width, _ = image_array.shape
            qimage = QImage(image_array.data, width, height, 3 * width, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            label.setPixmap(pixmap)
        except Exception as e:
            print(f"Error displaying image: {e}")

    def transmit_and_decode(self):
        if self.input_image is None:
            print("No image loaded. Please load an image first.")
            return

        try:
                coding_type = 1 if self.coding_select.currentText() == 'Hamming' else 2
                channel_model = 1 if self.channel_select.currentText() == 'BSC' else 2

                original_bits = image_to_bits(self.input_image)
                original_bit_count = original_bits.size
                image_parts = split_image(self.input_image)
                encoded_parts = [encode_data(image_to_bits(part), coding_type) for part in image_parts]
                transmitted_parts = []

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

                for encoded_data in encoded_parts:
                    if channel_model == 1:  # BSC
                        transmitted_data, _ = transmit_bsc(encoded_data, channel_params, coding_type,)
                    elif channel_model == 2:  # Gilbert-Elliott
                        transmitted_data, _ = transmit_gilbert_elliott(encoded_data, channel_params, coding_type)
                    else:
                        raise ValueError("Invalid channel model selected")

                    transmitted_parts.append(transmitted_data)

                noisy_non_decoded_bits = np.array(transmitted_parts).flatten()[:original_bit_count]
                noisy_non_decoded_image = bits_to_image(noisy_non_decoded_bits, self.input_image.shape)
                self.display_image(noisy_non_decoded_image, self.noisy_image_label)

                decode_args = [
                    (transmitted_data, coding_type, 3, part.shape)
                    for transmitted_data, part in zip(transmitted_parts, image_parts)
                ]
                with mp.Pool(processes=mp.cpu_count()) as pool:
                    decoded_parts = pool.map(decode_image_part, decode_args)

                final_image = merge_image(decoded_parts)

                self.display_image(final_image, self.decoded_image_label)
                overlay_image = self.generate_overlay_image(self.input_image, final_image)
                self.display_image(overlay_image, self.additional_image_label)
        except Exception as e:
            print(f"Error during transmission and decoding: {e}")

    def generate_overlay_image(self, input_image, output_image):
        """Overlay two images to highlight differences."""
        diff = np.abs(input_image - output_image)
        return diff.astype(np.uint8)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    simulator = TransmissionSimulator()
    simulator.show()
    sys.exit(app.exec())
