from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel
from .base import BasePanelWidget

class NavigationPanel(BasePanelWidget):
    def __init__(self, panel_id, title, bg, bus, controller):
        super().__init__(panel_id, title, bg, bus, controller)
        self.label = QLabel("WASD to set a course (stub)")
        self.label.setStyleSheet("color: #dfe8f1;")
        self.body_layout.addWidget(self.label)

    def keyPressEvent(self, e):
        key = e.key()
        if key in (Qt.Key_W, Qt.Key_A, Qt.Key_S, Qt.Key_D):
            direction = {Qt.Key_W: 'up', Qt.Key_S: 'down', Qt.Key_A: 'left', Qt.Key_D: 'right'}[key]
            self.bus.log.emit(f"[nav] plotting course {direction} (stub)")
        else:
            super().keyPressEvent(e)