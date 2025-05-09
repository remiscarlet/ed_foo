from datetime import datetime
from typing import Any

from pydantic import BaseModel

from src.core.models.body_model import Body
from src.core.models.common_model import Coordinates, Timestamps
from src.core.models.station_model import Station


class Faction(BaseModel):
    name: str
    influence: float | None = None
    government: str | None = None
    allegiance: str | None = None
    state: str | None = None

    edsm_id: int | None = None
    happiness: str | None = None
    is_player: bool | None = None
    active_states: list[str] | None = None
    pending_states: list[str] | None = None
    recovering_states: list[str] | None = None

    spansh_updated_at: datetime | None = None
    edsm_updated_at: datetime | None = None
    eddn_updated_at: datetime | None = None


class System(BaseModel):

    name: str
    coords: Coordinates
    date: datetime | None

    id64: int | None
    bodies: list[Body]
    allegiance: str | None
    factions: list[Faction]
    government: str | None
    population: int | None
    primary_economy: str | None
    secondary_economy: str | None
    security: str | None
    stations: list[Station]
    controlling_faction: Faction | None = None
    body_count: int | None = None
    controlling_power: str | None = None
    power_conflict_progress: list[Any] | None = None
    power_state: str | None = None
    power_state_control_progress: float | None = None
    power_state_reinforcement: float | None = None
    power_state_undermining: float | None = None
    powers: list[str] | None = None

    thargoid_war: dict[str, Any] | None = None
    timestamps: Timestamps | None = None

    controlling_power_updated_at: datetime | None = None
    power_state_updated_at: datetime | None = None
    powers_updated_at: datetime | None = None

    spansh_updated_at: datetime | None = None
    edsm_updated_at: datetime | None = None
    eddn_updated_at: datetime | None = None
