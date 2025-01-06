from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox, QFormLayout, QPushButton
from zoomable_label import ZoomableLabel

def create_main_layout(simulator):
    """
    Create the main GUI layout for the TransmissionSimulator application.

    :param simulator: Reference to the TransmissionSimulator instance.
    :return: Main layout (QHBoxLayout)
    """
    main_layout = QHBoxLayout()
    image_grid = QGridLayout()

    # Create image display labels
    simulator.input_image_label = ZoomableLabel()
    simulator.noisy_image_label = ZoomableLabel()
    simulator.decoded_image_label = ZoomableLabel()
    simulator.additional_image_label = ZoomableLabel()

    for label in [
        simulator.input_image_label,
        simulator.noisy_image_label,
        simulator.decoded_image_label,
        simulator.additional_image_label
    ]:
        label.setFixedSize(200, 400)
        label.setStyleSheet("border: 1px solid black;")

    # Add labels to the image grid
    image_grid.addWidget(simulator.input_image_label, 0, 0)
    image_grid.addWidget(simulator.noisy_image_label, 0, 1)
    image_grid.addWidget(simulator.decoded_image_label, 1, 0)
    image_grid.addWidget(simulator.additional_image_label, 1, 1)
    main_layout.addLayout(image_grid)

    # Create control layout
    control_layout = QVBoxLayout()
    select_layout = QHBoxLayout()

    simulator.channel_select = QComboBox()
    simulator.channel_select.addItems(['BSC', 'Gilbert-Elliott'])
    simulator.coding_select = QComboBox()
    simulator.coding_select.addItems(['Hamming', 'Convolutional'])

    select_layout.addWidget(QLabel("Select Coding Type"))
    select_layout.addWidget(simulator.coding_select)
    select_layout.addWidget(QLabel("Select Channel"))
    select_layout.addWidget(simulator.channel_select)
    control_layout.addLayout(select_layout)

    simulator.param_form = QFormLayout()
    simulator.param_inputs = {}
    control_layout.addLayout(simulator.param_form)

    simulator.load_btn = QPushButton('Load Image')
    control_layout.addWidget(simulator.load_btn)

    simulator.transmit_btn = QPushButton('Transmit & Decode')
    control_layout.addWidget(simulator.transmit_btn)

    main_layout.addLayout(control_layout)

    return main_layout
