from PyQt5.QtWidgets import QTextEdit
from .base import BasePanelWidget

class LogPanel(BasePanelWidget):
    def __init__(self, panel_id, title, bg, bus, controller):
        super().__init__(panel_id, title, bg, bus, controller)
        self.view = QTextEdit()
        self.view.setReadOnly(True)
        self.view.setStyleSheet("background: rgba(0,0,0,0.25); color: #e9f0f8;")
        self.body_layout.addWidget(self.view, 1)
        # Subscribe to logs
        self.bus.log.connect(self.append_line)

    def append_line(self, text: str):
        self.view.append(text)