from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel

from core.models.common_model import Coordinates, Timestamps


class Faction(BaseModel):
    name: str
    influence: float
    government: str
    allegiance: str
    state: str


class System(BaseModel):
    allegiance: str
    bodies: List[Any]  # Body
    controllingFaction: Any  # ControllingFaction
    coords: Coordinates
    date: datetime
    factions: List[Any]  #  PlayerMinorFaction
    government: str
    id64: int
    name: str
    population: int
    primaryEconomy: str
    secondaryEconomy: str
    security: str
    stations: List[Any]  # Station

    bodyCount: Optional[int] = None

    controllingPower: Optional[str] = None
    powerConflictProgress: Optional[List[Any]] = None
    powerState: Optional[str] = None
    powerStateControlProgress: Optional[float] = None
    powerStateReinforcement: Optional[float] = None
    powerStateUndermining: Optional[float] = None
    powers: Optional[List[str]] = None

    thargoidWar: Optional[int] = None
    timestamps: Optional[Timestamps] = None
