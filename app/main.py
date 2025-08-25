import argparse
from pathlib import Path
from typing import Dict, Type

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QStatusBar, QShortcut
from PyQt5.QtGui import QKeySequence

from .config import load_config
from .game_state import GameState
from .controller import EventBus, MainController
from .widgets.nav_panel import NavigationPanel
from .widgets.scan_panel import ScanPanel
from .widgets.comms_panel import CommsPanel
from .widgets.log_panel import LogPanel

WIDGET_REGISTRY: Dict[str, Type[QWidget]] = {
    "NavigationPanel": NavigationPanel,
    "ScanPanel": ScanPanel,
    "CommsPanel": CommsPanel,
    "LogPanel": LogPanel,
}

class MainWindow(QMainWindow):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.bus = EventBus()
        self.state = GameState()
        self.controller = MainController(self.state, self.bus)

        # Status bar shows turn + focus
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._focused_panel = "—"
        self._update_status()
        self.bus.turn_changed.connect(lambda t: self._update_status())
        self.bus.focus_changed.connect(self._on_focus_changed)

        # Central grid per config
        cw = QWidget()
        grid = QGridLayout(cw)
        grid.setContentsMargins(6, 6, 6, 6)
        grid.setSpacing(6)

        # Row/col stretch
        rows = cfg["layout"].get("rows", 2)
        cols = cfg["layout"].get("cols", 2)
        for r, s in enumerate(cfg["layout"].get("row_stretch", [1]*rows)):
            grid.setRowStretch(r, int(s))
        for c, s in enumerate(cfg["layout"].get("col_stretch", [1]*cols)):
            grid.setColumnStretch(c, int(s))

        # Build panels
        for p in cfg.get("panels", []):
            clsname = p.get("widget", "LogPanel")
            PanelCls = WIDGET_REGISTRY.get(clsname, LogPanel)
            w = PanelCls(p.get("id", "panel"), p.get("title", "Panel"), p.get("bg", "#111"), self.bus, self.controller)
            grid.addWidget(w, int(p.get("row", 0)), int(p.get("col", 0)))

        self.setCentralWidget(cw)

        # Global shortcuts
        QShortcut(QKeySequence("E"), self, activated=self.controller.advance_turn)
        QShortcut(QKeySequence(Qt.Key_Return), self, activated=self.controller.advance_turn)

        # Window settings
        win = cfg.get("window", {})
        self.setWindowTitle(win.get("title", "SpaceGame — Phase 1"))
        self.resize(int(win.get("width", 1200)), int(win.get("height", 800)))

    def _on_focus_changed(self, panel_id: str):
        self._focused_panel = panel_id
        self._update_status()

    def _update_status(self):
        self.status.showMessage(f"Turn: {self.state.turn}    Focus: {self._focused_panel}")


def main():
    parser = argparse.ArgumentParser(description="SpaceGame (Phase 1)")
    parser.add_argument("--config", type=str, default=str(Path(__file__).resolve().parent.parent / "config" / "config.json"))
    args = parser.parse_args()

    cfg = load_config(args.config)

    app = QApplication([])
    win = MainWindow(cfg)
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()