from PyQt5.QtCore import QObject, pyqtSignal
from .game_state import GameState

class EventBus(QObject):
    log = pyqtSignal(str)
    turn_changed = pyqtSignal(int)
    focus_changed = pyqtSignal(str)

class MainController(QObject):
    def __init__(self, state: GameState, bus: EventBus):
        super().__init__()
        self.state = state
        self.bus = bus

    def advance_turn(self):
        new_turn = self.state.advance_turn()
        self.bus.turn_changed.emit(new_turn)
        self.bus.log.emit(f"Turn advanced to {new_turn}")