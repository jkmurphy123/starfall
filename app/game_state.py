from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class GameState:
    turn: int = 1
    # Room for more state as the game grows
    ship: Dict[str, Any] = field(default_factory=lambda: {"fuel": 100, "hull": 100, "credits": 0})
    location: Dict[str, Any] = field(default_factory=lambda: {"system": "Sol", "planet": "Earth"})

    def advance_turn(self) -> int:
        self.turn += 1
        return self.turn