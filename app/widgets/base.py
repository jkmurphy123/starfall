from typing import Optional
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame

class BasePanelWidget(QWidget):
    """Common behavior for all panels: title bar, focus border, bg color, input hooks."""
    def __init__(self, panel_id: str, title: str, bg: str, bus, controller):
        super().__init__()
        self.panel_id = panel_id
        self.title = title
        self.bg = bg
        self.bus = bus
        self.controller = controller

        # Visuals
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(bg))
        self.setPalette(pal)

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(8, 8, 8, 8)
        self.root.setSpacing(8)

        self.header = QLabel(self.title)
        self.header.setStyleSheet("font-weight: 600; color: #9ad0ff; letter-spacing: 0.5px;")
        self.root.addWidget(self.header)

        self.body = QFrame()
        self.body.setFrameShape(QFrame.NoFrame)
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(8, 8, 8, 8)
        self.body_layout.setSpacing(6)
        self.root.addWidget(self.body, 1)

        self.hint = QLabel("Click to focus; press E to end turn (global). Panel-specific keys vary.")
        self.hint.setStyleSheet("color: #b7c2cc; font-size: 11px;")
        self.root.addWidget(self.hint)

        self.bus.turn_changed.connect(self.on_turn_changed)

    # --- Focus visuals ---
    def focusInEvent(self, event):
        self.setStyleSheet("border: 2px solid #5cc8ff; border-radius: 6px;")
        self.bus.focus_changed.emit(self.panel_id)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.setStyleSheet("")
        super().focusOutEvent(event)

    # --- Input hooks ---
    def keyPressEvent(self, e):
        # Default behavior: just log key name.
        self.bus.log.emit(f"[{self.panel_id}] key: {e.text() or e.key()}")

    def mousePressEvent(self, e):
        self.setFocus()
        self.bus.log.emit(f"[{self.panel_id}] mouse at ({int(e.x())},{int(e.y())})")
        super().mousePressEvent(e)

    # --- Game hooks ---
    def on_turn_changed(self, turn: int):
        # Children may override.
        pass