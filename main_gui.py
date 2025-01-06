import sys
from PySide6.QtWidgets import QApplication
from desktop.TransmissionSimulator import TransmissionSimulator

if __name__ == '__main__':
    app = QApplication(sys.argv)
    simulator = TransmissionSimulator()
    simulator.show()
    sys.exit(app.exec())
