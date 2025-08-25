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

# creating the database

# wherever you initialize the app (e.g., in MainController.__init__)
from .db import make_engine, create_db_and_tables, get_session, seed_projects_if_empty
engine = make_engine("sqlite:///spacegame.db", echo=False)
create_db_and_tables(engine)
with get_session(engine) as s:
    seed_projects_if_empty(s)
