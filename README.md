# starfall
Space exploration game

spacegame/
├─ app/
│ ├─ __init__.py
│ ├─ main.py
│ ├─ config.py
│ ├─ game_state.py
│ ├─ controller.py
│ ├─ llm_client.py # (stub for Phase 2)
│ ├─ db.py # (stub for Phase 3)
│ └─ widgets/
│ ├─ __init__.py
│ ├─ base.py
│ ├─ nav_panel.py
│ ├─ scan_panel.py
│ ├─ comms_panel.py
│ └─ log_panel.py
├─ config/
│ └─ config.json
└─ requirements.txt

# 1) Create & activate a venv (example)
cd projects
python3 -m venv llm_env
source llm_env/bin/activate  
cd starfall

# 2) Install deps
pip install -r requirements.txt

# 3) Launch
python -m app.main --config config/config.json