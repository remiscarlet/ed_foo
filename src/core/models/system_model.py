from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from src.core.models.body_model import Body
from src.core.models.common_model import Coordinates, Timestamps
from src.core.models.station_model import Station


class Faction(BaseModel):
    name: str
    influence: Optional[float] = None
    government: Optional[str] = None
    allegiance: Optional[str] = None
    state: Optional[str] = None

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
    id64: int
    name: str
    coords: Coordinates
    date: Optional[datetime]

    bodies: List[Body]
    allegiance: Optional[str]
    factions: List[Faction]
    government: Optional[str]
    population: Optional[int]
    primary_economy: Optional[str]
    secondary_economy: Optional[str]
    security: Optional[str]
    stations: List[Station]
    controlling_faction: Optional[Faction] = None
    body_count: Optional[int] = None
    controlling_power: Optional[str] = None
    power_conflict_progress: Optional[List[Any]] = None
    power_state: Optional[str] = None
    power_state_control_progress: Optional[float] = None
    power_state_reinforcement: Optional[float] = None
    power_state_undermining: Optional[float] = None
    powers: Optional[List[str]] = None

    thargoid_war: Optional[Dict[str, Any]] = None
    timestamps: Optional[Timestamps] = None

    controlling_power_updated_at: Optional[datetime] = None
    power_state_updated_at: Optional[datetime] = None
    powers_updated_at: Optional[datetime] = None

    spansh_updated_at: Optional[datetime] = None
    edsm_updated_at: Optional[datetime] = None
    eddn_updated_at: Optional[datetime] = None
