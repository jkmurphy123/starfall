import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG = {
    "window": {"width": 1200, "height": 800, "title": "SpaceGame — Phase 1 (Default)"},
    "layout": {"rows": 2, "cols": 2, "row_stretch": [1, 1], "col_stretch": [1, 1]},
    "panels": [
        {"id": "nav",   "title": "Navigation", "row": 0, "col": 0, "bg": "#0b1a2b", "widget": "NavigationPanel"},
        {"id": "scan",  "title": "Scanner",    "row": 0, "col": 1, "bg": "#132233", "widget": "ScanPanel"},
        {"id": "comms", "title": "Comms",      "row": 1, "col": 0, "bg": "#14202d", "widget": "CommsPanel"},
        {"id": "log",   "title": "Log",        "row": 1, "col": 1, "bg": "#0f1822", "widget": "LogPanel"}
    ]
}


def load_config(path: str | Path | None) -> Dict[str, Any]:
    """Load a JSON config; fall back to DEFAULT_CONFIG if not found/invalid."""
    if path is None:
        return DEFAULT_CONFIG
    p = Path(path)
    if not p.exists():
        print(f"[config] Missing {p!s}; using defaults")
        return DEFAULT_CONFIG
    try:
        return json.loads(p.read_text())
    except Exception as e:
        print(f"[config] Failed to parse {p!s}: {e}; using defaults")
        return DEFAULT_CONFIG