import sys
from PySide6.QtWidgets import QApplication
from gui_components import create_main_layout  # Custom function to create GUI layout
from image_processing import process_image  # Custom function for image processing
from TransmissionSimulator import TransmissionSimulator

if __name__ == '__main__':
    app = QApplication(sys.argv)
    simulator = TransmissionSimulator()
    simulator.show()
    sys.exit(app.exec())
