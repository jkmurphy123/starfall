from typing import Dict, Any, List
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QPushButton, QMenu, QAction, QHBoxLayout, QVBoxLayout
from .base import BasePanelWidget

class CommandsPanel(BasePanelWidget):
    """Command Console: left-side top-level buttons; hover opens nested menus (3 levels).
    Menu structure is provided via the panel's config as a `menu` list.
    Each leaf item has `actions`: [{"panel_id": "nav", "method": "board_ship", "args": [...], "kwargs": {...}}, ...]
    """
    def __init__(self, panel_id, title, bg, bus, controller):
        super().__init__(panel_id, title, bg, bus, controller)
        self.widget_registry: Dict[str, BasePanelWidget] = {}
        self.panel_cfg: Dict[str, Any] = {}

        # Layout: left column of buttons
        self.columns = QHBoxLayout()
        self.body_layout.addLayout(self.columns)
        self.left = QVBoxLayout()
        self.left.setSpacing(6)
        self.columns.addLayout(self.left, 0)
        self.columns.addStretch(1)

        self.info = QLabel("Hover a command, then click an item to execute.")
        self.info.setStyleSheet("color: #dfe8f1;")
        self.body_layout.addWidget(self.info)

    # hooks from MainWindow
    def set_widget_registry(self, registry: Dict[str, BasePanelWidget]):
        self.widget_registry = registry

    def set_panel_config(self, cfg: Dict[str, Any]):
        self.panel_cfg = cfg or {}
        self._rebuild()

    # UI building
    def _rebuild(self):
        # clear
        while self.left.count():
            item = self.left.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        for spec in self.panel_cfg.get("menu", []):
            btn = _HoverMenuButton(spec.get("label", "Command"), self)
            btn.set_menu(self._make_menu(spec))
            self.left.addWidget(btn)
        self.left.addStretch(1)

    def _make_menu(self, top_spec: Dict[str, Any]) -> QMenu:
        m = QMenu(self)
        for mid in top_spec.get("children", []):
            sub = QMenu(mid.get("label", ""), m)
            for leaf in mid.get("children", []):
                act = QAction(leaf.get("label", ""), sub)
                act.triggered.connect(lambda _=False, data=leaf: self._execute_actions(data))
                sub.addAction(act)
            m.addMenu(sub)
        return m

    def _execute_actions(self, leaf: Dict[str, Any]):
        actions: List[Dict[str, Any]] = leaf.get("actions", [])
        if not actions:
            self.bus.log.emit("[commands] No actions configured for this item.")
            return
        for a in actions:
            panel_id = a.get("panel_id")
            widget_name = a.get("widget")
            method_name = a.get("method")
            args = a.get("args", [])
            kwargs = a.get("kwargs", {})
            target = None
            if panel_id and self.widget_registry:
                target = self.widget_registry.get(panel_id)
            if target is None and widget_name and self.widget_registry:
                for w in self.widget_registry.values():
                    if w.__class__.__name__ == widget_name:
                        target = w
                        break
            if target and hasattr(target, method_name):
                try:
                    getattr(target, method_name)(*args, **kwargs)
                except Exception as e:
                    self.bus.log.emit(f"[commands] Error calling {method_name} on {getattr(target,'panel_id','?')}: {e}")
            else:
                self.bus.log.emit(f"[commands] Cannot dispatch action: {a}")

class _HoverMenuButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self._menu: QMenu | None = None
        self.setStyleSheet(
            "QPushButton{padding:8px 10px; text-align:left; background:#203040; color:#dfe8f1;"
            " border:1px solid #2b425a; border-radius:6px;}"
            "QPushButton:hover{background:#2a3f5a;}"
        )
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)
        self.clicked.connect(self.show_menu)

    def set_menu(self, menu: QMenu):
        self._menu = menu

    def enterEvent(self, e):
        self.show_menu()
        super().enterEvent(e)

    def show_menu(self):
        if self._menu:
            pos = self.mapToGlobal(self.rect().topRight())
            self._menu.popup(pos)
