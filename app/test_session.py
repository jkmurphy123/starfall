from sqlmodel import SQLModel, Session, create_engine, select
from models.player import Player
from models.location_assessment import LocationAssessment

engine = create_engine("sqlite:///test.db", echo=False)
SQLModel.metadata.create_all(engine)

with Session(engine) as s:
    p = Player(name="Ada")
    s.add(p); s.commit(); s.refresh(p)
    s.add(LocationAssessment(score=42, player=p)); s.commit()
    got = s.exec(select(Player)).first()
    print(len(got.assessments))  # -> 1
