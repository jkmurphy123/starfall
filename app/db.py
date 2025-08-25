"""
Relational data model for SpaceGame using SQLModel (SQLAlchemy under the hood).
Covers: players, assets (materials, technologies), star systems, locations,
features (incl. plots, establishments, ruins, artifacts, POIs), assessments,
plot surveys, deeds, Projects & Tasks, and helpers for engine/session creation.
"""
from __future__ import annotations
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, List

from sqlmodel import (
    SQLModel,
    Field,
    Relationship,
    Session,
    create_engine,
    select,
)
from sqlalchemy import Column, UniqueConstraint

try:
    from sqlalchemy import JSON  # SA>=1.4 has JSON (mapped to TEXT on SQLite)
except Exception:  # pragma: no cover
    JSON = None  # type: ignore

# -----------------------------
# Enums
# -----------------------------
class LocationKind(str, Enum):
    PLANET = "planet"
    MOON = "moon"
    ASTEROID = "asteroid"
    STATION = "space_station"
    ALIEN_CONSTRUCT = "alien_construct"
    NEBULA = "nebula"

class FeatureKind(str, Enum):
    PLOT = "plot"
    ESTABLISHMENT = "establishment"
    RUINS = "ruins"
    ALIEN_ARTIFACT = "alien_artifact"
    POI = "point_of_interest"

class TechStatus(str, Enum):
    BLUEPRINT = "blueprint"
    RESEARCHED = "researched"
    BUILT = "built"

# Projects / Tasks
class TaskStatus(str, Enum):
    UNASSIGNED = "unassigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# -----------------------------
# Utility
# -----------------------------
_ROMANS = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
    (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
]

def to_roman(n: int) -> str:
    if n <= 0:
        return str(n)
    result = []
    for val, sym in _ROMANS:
        while n >= val:
            result.append(sym)
            n -= val
    return "".join(result)

# -----------------------------
# Core game entities
# -----------------------------
class StarSystem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    description: str = ""

    locations: List["Location"] = Relationship(back_populates="system")  # defined later

class Location(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    system_id: int = Field(foreign_key="starsystem.id", index=True)
    kind: LocationKind
    ordinal: int = 1  # Used to display Roman numeral with system name
    name: str = ""  # Optional short name (e.g., "Gaia"); display_name is property
    description: str = ""
    image_path: str = ""

    system: Optional["StarSystem"] = Relationship(back_populates="locations")
    features: List["Feature"] = Relationship(back_populates="location")

    __table_args__ = (
        UniqueConstraint("system_id", "ordinal", name="uix_location_system_ordinal"),
    )

    @property
    def display_name(self) -> str:
        # E.g., "Sol IV"; includes optional nickname if provided
        base = f"{self.system.name if self.system else 'Unknown'} {to_roman(self.ordinal)}"
        return f"{base} — {self.name}" if self.name else base

class Feature(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    location_id: int = Field(foreign_key="location.id", index=True)
    kind: FeatureKind
    name: str = ""  # e.g., "Trading Post", "Obelisk A", "North Ridge"
    description: str = ""
    discovered_turn: int = 0
    meta: Dict = Field(default_factory=dict, sa_column=Column(JSON) if JSON else None)

    location: Optional["Location"] = Relationship(back_populates="features")
    plot: Optional["Plot"] = Relationship(back_populates="feature", sa_relationship_kwargs={"uselist": False})

# -----------------------------
# Plots & deeds & surveys
# -----------------------------
class Plot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    feature_id: int = Field(foreign_key="feature.id", unique=True)
    size_hectares: float = 1.0
    quality: int = 0  # abstract quality score 0–100

    feature: Optional["Feature"] = Relationship(back_populates="plot")
    deed: Optional["Deed"] = Relationship(back_populates="plot", sa_relationship_kwargs={"uselist": False})
    materials: List["PlotMaterial"] = Relationship(back_populates="plot")
    surveys: List["PlotSurvey"] = Relationship(back_populates="plot")

class Deed(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    plot_id: int = Field(foreign_key="plot.id", unique=True)
    owner_id: int = Field(foreign_key="player.id", index=True)
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    price: int = 0
    notes: str = ""

    plot: Optional["Plot"] = Relationship(back_populates="deed")
    owner: Optional["Player"] = Relationship(back_populates="deeds")

class Material(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    rarity: int = 1  # 1 common … 5 legendary
    unit: str = "kg"
    description: str = ""

    plot_links: List["PlotMaterial"] = Relationship(back_populates="material")
    recipe_links: List["TechRecipeItem"] = Relationship(back_populates="material")

class PlotMaterial(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    plot_id: int = Field(foreign_key="plot.id", index=True)
    material_id: int = Field(foreign_key="material.id", index=True)
    quantity: float = 0.0  # in material.unit

    plot: Optional["Plot"] = Relationship(back_populates="materials")
    material: Optional["Material"] = Relationship(back_populates="plot_links")

class PlotSurvey(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    plot_id: int = Field(foreign_key="plot.id", index=True)
    player_id: int = Field(foreign_key="player.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confidence: int = 75  # 0–100
    notes: str = ""

    plot: Optional["Plot"] = Relationship(back_populates="surveys")
    player: Optional["Player"] = Relationship(back_populates="surveys")
    materials: List["PlotSurveyMaterial"] = Relationship(back_populates="survey")

class PlotSurveyMaterial(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    survey_id: int = Field(foreign_key="plotsurvey.id", index=True)
    material_id: int = Field(foreign_key="material.id")
    estimated_qty: float = 0.0
    grade: str = ""  # freeform (e.g., "high purity", "trace")

    survey: Optional["PlotSurvey"] = Relationship(back_populates="materials")
    material: Optional["Material"] = Relationship()

# -----------------------------
# Technology & crafting
# -----------------------------
class Technology(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(index=True, unique=True)  # e.g., "extractor_mk1"
    name: str
    description: str = ""
    image_path: str = ""

    recipe_items: List["TechRecipeItem"] = Relationship(back_populates="technology")

class TechRecipeItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    technology_id: int = Field(foreign_key="technology.id", index=True)
    material_id: int = Field(foreign_key="material.id")
    quantity: float = 0.0

    technology: Optional["Technology"] = Relationship(back_populates="recipe_items")
    material: Optional["Material"] = Relationship(back_populates="recipe_links")

class PlayerTechnology(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="player.id", index=True)
    technology_id: int = Field(foreign_key="technology.id", index=True)
    status: TechStatus = Field(default=TechStatus.BLUEPRINT)
    acquired_turn: int = 0

    player: Optional["Player"] = Relationship(back_populates="technologies")
    technology: Optional["Technology"] = Relationship()

# -----------------------------
# Player inventory (materials)
# -----------------------------
class PlayerMaterial(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("player_id", "material_id", name="uix_player_material"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="player.id", index=True)
    material_id: int = Field(foreign_key="material.id", index=True)
    quantity: float = 0.0

    player: Optional[Player] = Relationship(back_populates="inventory")
    material: Optional[Material] = Relationship()

# -----------------------------
# Knowledge capture
# -----------------------------
class LocationAssessment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    location_id: int = Field(foreign_key="location.id", index=True)
    player_id: int = Field(foreign_key="player.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    summary: str = ""
    details_text: str = ""  # full description (possibly LLM generated)
    data: Dict = Field(default_factory=dict, sa_column=Column(JSON) if JSON else None)  # structured extras

    location: Optional[Location] = Relationship()
    player: Optional[Player] = Relationship(back_populates="assessments")

class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    credits: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    deeds: List[Deed] = Relationship(back_populates="owner")  # defined later
    inventory: List[PlayerMaterial] = Relationship(back_populates="player")
    technologies: List[PlayerTechnology] = Relationship(back_populates="player")
    assessments: List[LocationAssessment] = Relationship(back_populates="player")
    surveys: List[PlotSurvey] = Relationship(back_populates="player")

# -----------------------------
# Projects & Tasks (player guide)
# -----------------------------
class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(index=True, unique=True)
    name: str
    description: str = ""

    tasks: List["Task"] = Relationship(back_populates="project")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", index=True)
    key: str = Field(index=True)
    name: str
    description: str = ""
    order_index: int = 0
    status: TaskStatus = Field(default=TaskStatus.UNASSIGNED)
    hidden: bool = True  # hidden until revealed by progression

    project: Optional["Project"] = Relationship(back_populates="tasks")

    __table_args__ = (
        UniqueConstraint("project_id", "key", name="uix_task_proj_key"),
    )

# -----------------------------
# Engine / session helpers
# -----------------------------
_DEF_URL = "sqlite:///spacegame.db"

def make_engine(db_url: str = _DEF_URL, echo: bool = False):
    """Create a SQLAlchemy engine. Default is SQLite file in CWD."""
    return create_engine(db_url, echo=echo)

def create_db_and_tables(engine) -> None:
    SQLModel.metadata.create_all(engine)

def get_session(engine) -> Session:
    return Session(engine)

# -----------------------------
# Convenience queries (examples)
# -----------------------------
def get_or_create_system(session: Session, name: str, **coords) -> StarSystem:
    sys = session.exec(select(StarSystem).where(StarSystem.name == name)).first()
    if not sys:
        sys = StarSystem(name=name, **{"x": 0.0, "y": 0.0, "z": 0.0} | coords)
        session.add(sys)
        session.commit()
        session.refresh(sys)
    return sys

def create_location(session: Session, system: StarSystem, kind: LocationKind, ordinal: int, **kwargs) -> Location:
    loc = Location(system_id=system.id, kind=kind, ordinal=ordinal, **kwargs)
    session.add(loc)
    session.commit()
    session.refresh(loc)
    return loc

# -----------------------------
# Seed helper for Projects & Tasks
# -----------------------------
def seed_projects_if_empty(session: Session) -> None:
    """Seed a couple of starter projects with hidden tasks if DB is empty."""
    has_any = session.exec(select(Project)).first()
    if has_any:
        return

    p1 = Project(key="getting_started", name="Getting Started", description="Basic ship bring-up sequence.")
    p2 = Project(key="first_scout", name="First Scout Mission", description="Perform a short systems check and scan.")

    session.add(p1); session.add(p2)
    session.commit(); session.refresh(p1); session.refresh(p2)

    def add_task(p: Project, key: str, name: str, desc: str, idx: int,
                 status: TaskStatus = TaskStatus.UNASSIGNED, hidden: bool = True):
        t = Task(project_id=p.id, key=key, name=name, description=desc,
                 order_index=idx, status=status, hidden=hidden)
        session.add(t)

    # Getting Started
    add_task(p1, "board_ship", "Board your ship", "Head to the docking bay and board.", 1)
    add_task(p1, "power_up", "Power up systems", "Restore main power and run diagnostics.", 2)
    add_task(p1, "undock", "Undock from station", "Request clearance and undock safely.", 3)

    # First Scout
    add_task(p2, "plot_course", "Plot short course", "WASD to pick a safe training vector.", 1)
    add_task(p2, "short_scan", "Run a short-range scan", "Tap Space to ping local area.", 2)

    session.commit()
