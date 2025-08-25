from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel
from .base import BasePanelWidget

class CommsPanel(BasePanelWidget):
    def __init__(self, panel_id, title, bg, bus, controller):
        super().__init__(panel_id, title, bg, bus, controller)
        self.label = QLabel("C to hail; H to open channel (stub)")
        self.label.setStyleSheet("color: #dfe8f1;")
        self.body_layout.addWidget(self.label)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_C:
            self.bus.log.emit("[comms] sending standard hail... (stub)")
        elif e.key() == Qt.Key_H:
            self.bus.log.emit("[comms] opening channel... (stub)")
        else:
            super().keyPressEvent(e)