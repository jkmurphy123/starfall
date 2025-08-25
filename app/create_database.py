from db import make_engine, create_db_and_tables, get_session, seed_projects_if_empty

engine = make_engine("sqlite:///spacegame.db", echo=False)
create_db_and_tables(engine)

with get_session(engine) as s:
    seed_projects_if_empty(s)