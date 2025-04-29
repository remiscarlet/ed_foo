from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel

from src.core.models.common_model import Coordinates, Timestamps


class Faction(BaseModel):
    name: str
    influence: float
    government: str
    allegiance: str
    state: str

    edsm_id: Optional[int] = None
    happiness: Optional[str] = None
    is_player: Optional[bool] = None
    active_states: Optional[List[str]] = None
    pending_states: Optional[List[str]] = None
    recovering_states: Optional[List[str]] = None

    spansh_updated_at: Optional[datetime] = None
    edsm_updated_at: Optional[datetime] = None
    eddn_updated_at: Optional[datetime] = None


class System(BaseModel):
    allegiance: str
    bodies: List[Any]  # Body
    controlling_faction: Any  # ControllingFaction
    coords: Coordinates
    date: datetime
    factions: List[Any]  # PlayerMinorFaction
    government: str
    id64: int
    name: str
    population: int
    primary_economy: str
    secondary_economy: str
    security: str
    stations: List[Any]  # Station

    body_count: Optional[int] = None

    controlling_power: Optional[str] = None
    power_conflict_progress: Optional[List[Any]] = None
    power_state: Optional[str] = None
    power_state_control_progress: Optional[float] = None
    power_state_reinforcement: Optional[float] = None
    power_state_undermining: Optional[float] = None
    powers: Optional[List[str]] = None

    thargoid_war: Optional[int] = None
    timestamps: Optional[Timestamps] = None

    spansh_updated_at: Optional[datetime] = None
    edsm_updated_at: Optional[datetime] = None
    eddn_updated_at: Optional[datetime] = None
