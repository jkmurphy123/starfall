from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel
from .base import BasePanelWidget

class ScanPanel(BasePanelWidget):
    def __init__(self, panel_id, title, bg, bus, controller):
        super().__init__(panel_id, title, bg, bus, controller)
        self.label = QLabel("Spacebar to run scanner (stub)")
        self.label.setStyleSheet("color: #dfe8f1;")
        self.body_layout.addWidget(self.label)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Space:
            self.bus.log.emit("[scan] scanning local space... (stub)")
        else:
            super().keyPressEvent(e)

    def on_turn_changed(self, turn: int):
        self.bus.log.emit(f"[scan] passive sensors updated for turn {turn}")

    # ---- Exposed actions (for CommandsPanel) ----
    def show_location(self):
        self.bus.log.emit("[scan] Displaying current location overview… (stub action)")
        return True        