from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QPainter, QWheelEvent, QMouseEvent
from PySide6.QtCore import Qt, QPoint

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

