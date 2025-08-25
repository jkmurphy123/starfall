# controller.py
from typing import Dict, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal
from .game_state import GameState

# NEW imports
from .db import make_engine, create_db_and_tables, get_session, seed_projects_if_empty
from .task_service import TaskService

class EventBus(QObject):
    log = pyqtSignal(str)
    turn_changed = pyqtSignal(int)
    focus_changed = pyqtSignal(str)
    action_called = pyqtSignal(str)  # e.g., "nav.board_ship()"

class MainController(QObject):
    def __init__(self, state: GameState, bus: EventBus, cfg: dict):
        super().__init__()
        self.state = state
        self.bus = bus
        self.cfg = cfg
        self._widgets: Dict[str, QObject] = {}

        # --- NEW: DB + Tasks wiring ---
        db_url = cfg.get("db_url", "sqlite:///spacegame.db")
        self.engine = make_engine(db_url=db_url, echo=bool(cfg.get("db_echo", False)))
        create_db_and_tables(self.engine)

        # Seed starter projects/tasks only if empty
        with get_session(self.engine) as s:
            seed_projects_if_empty(s)

        self.tasks = TaskService(lambda: get_session(self.engine))

    # ---- Turn mgmt ----
    def advance_turn(self):
        new_turn = self.state.advance_turn()
        self.bus.turn_changed.emit(new_turn)
        self.bus.log.emit(f"Turn advanced to {new_turn}")

    # ---- Widget registry ----
    def register_widget(self, panel_id: str, widget: QObject):
        self._widgets[panel_id] = widget

    def resolve_widget(self, panel_id: str) -> Optional[QObject]:
        return self._widgets.get(panel_id)

    # ---- Command actions ----
    def call_action(self, panel_id: str, method: str, *args, **kwargs) -> Any:
        target = self.resolve_widget(panel_id)
        if not target:
            self.bus.log.emit(f"[commands] Unknown widget id: {panel_id}")
            return None
        fn = getattr(target, method, None)
        if not callable(fn):
            self.bus.log.emit(f"[commands] Widget '{panel_id}' has no method '{method}'")
            return None
        self.bus.action_called.emit(f"{panel_id}.{method}()")
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            self.bus.log.emit(f"[commands] Error calling {panel_id}.{method}: {e}")
            return None
