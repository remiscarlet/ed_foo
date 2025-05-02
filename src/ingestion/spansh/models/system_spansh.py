from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from src.ingestion.spansh.models import BaseSpanshModel
from src.ingestion.spansh.models.body_spansh import BodySpansh
from src.ingestion.spansh.models.common_spansh import (
    CoordinatesSpansh,
    TimestampsSpansh,
)
from src.ingestion.spansh.models.station_spansh import StationSpansh


class ThargoidWarSpansh(BaseSpanshModel):
    current_state: str
    days_remaining: float
    failure_state: str
    ports_remaining: float
    progress: float
    success_reached: bool
    success_state: str

    def to_cache_key_tuple(self) -> Tuple[Any, ...]:
        return (
            self.__class__,
            self.current_state,
            self.days_remaining,
            self.failure_state,
            self.ports_remaining,
            self.progress,
            self.success_reached,
            self.success_state,
        )

    def to_sqlalchemy_dict(self) -> Dict[str, Any]:
        return {
            "current_state": self.current_state,
            "days_remaining": self.days_remaining,
            "failure_state": self.failure_state,
            "ports_remaining": self.ports_remaining,
            "progress": self.progress,
            "success_reached": self.success_reached,
            "success_state": self.success_state,
        }


class FactionSpansh(BaseSpanshModel):
    name: str
    influence: Optional[float]

    government: Optional[str] = None
    allegiance: Optional[str] = None
    state: Optional[str] = None

    def to_cache_key_tuple(self) -> Tuple[Any, ...]:
        return (self.__class__, self.name)

    def to_sqlalchemy_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "allegiance": self.allegiance,
            "government": self.government,
            "influence": self.influence,
            "state": self.state,
        }


class ControllingFactionSpansh(BaseSpanshModel):
    name: str
    allegiance: Optional[str] = None
    government: Optional[str] = None

    def to_cache_key_tuple(self) -> Tuple[Any, ...]:
        return (FactionSpansh, self.name)

    def to_sqlalchemy_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "allegiance": self.allegiance,
            "government": self.government,
        }


class PowerConflictProgressSpansh(BaseSpanshModel):
    power: str
    progress: float

    def to_sqlalchemy_dict(self) -> Dict[str, Any]:
        return {
            "power": self.power,
            "progress": self.progress,
        }


class SystemSpansh(BaseSpanshModel):
    def __repr__(self) -> str:
        return (
            f"SystemSpansh(id64: {self.id64}, name: {self.name}, "
            f"allegiance: {self.allegiance}, coords: {self.coords})"
        )

    def to_cache_key_tuple(self) -> Tuple[Any, ...]:
        return ("SystemsDB", self.name)

    id64: int
    name: str

    allegiance: str
    coords: CoordinatesSpansh
    date: datetime
    _validate_date = BaseSpanshModel.flexible_datetime_validator("date")

    controlling_faction: Optional[ControllingFactionSpansh]
    government: Optional[str] = None
    population: Optional[int] = None
    primary_economy: Optional[str] = None
    secondary_economy: Optional[str] = None
    security: Optional[str] = None

    bodies: Optional[List[BodySpansh]] = None
    factions: Optional[List[FactionSpansh]] = None
    all_stations: Optional[List[StationSpansh]] = None

    body_count: Optional[int] = None

    controlling_power: Optional[str] = None
    power_conflict_progress: Optional[List[PowerConflictProgressSpansh]] = None
    power_state: Optional[str] = None
    power_state_control_progress: Optional[float] = None
    power_state_reinforcement: Optional[float] = None
    power_state_undermining: Optional[float] = None
    powers: Optional[List[str]] = None

    thargoid_war: Optional[ThargoidWarSpansh] = None
    timestamps: Optional[TimestampsSpansh] = None

    @property
    def stations(self) -> Optional[List[StationSpansh]]:
        """Systems can only have one active System Colonisation Ship at a time.
        SCS's can also be decommissioned if not "fulfilled in time".
        Each newly commissioned SCS after previous iterations fail are considered new stations/entities
        Data aggregation sites like EDSM/Spansh don't de-duplicate;they keep
        historic 'no-longer-active' SCS's in their data
        Aside from the internal id64 that the game uses,
        we don't actually have a way to distinguish these dupe/decommisioned SCS's from the active SCS
        As such the best workaround is that if there are multiple SCS's in a given system from a datadump,
        just take the newest one, even though the newest one might also technically be decommissioned.

        SCS's are only ever system-level stations - never planetary stations.
        """
        if self.all_stations is None:
            return None

        stations = []
        colonisation_ships = []
        for station in self.all_stations:
            if station.name == "System Colonisation Ship":
                colonisation_ships.append(station)
            else:
                stations.append(station)
        newest_scs = max(
            colonisation_ships,
            key=lambda scs: (scs.updated_at if scs.updated_at is not None else datetime(year=1, month=1, day=1)),
        )
        if newest_scs:
            stations.append(newest_scs)

        return stations

    def to_sqlalchemy_dict(self, controlling_faction_id: Optional[int]) -> Dict[str, Any]:
        return {
            "allegiance": self.allegiance,
            "controlling_faction_id": controlling_faction_id,
            "x": self.coords.x,
            "y": self.coords.y,
            "z": self.coords.z,
            "date": self.date,
            "government": self.government,
            "id64": self.id64,
            "name": self.name,
            "population": self.population,
            "primary_economy": self.primary_economy,
            "secondary_economy": self.secondary_economy,
            "security": self.security,
            "body_count": self.body_count,
            "controlling_power": self.controlling_power,
            "power_conflict_progress": [
                participant.to_sqlalchemy_dict() for participant in self.power_conflict_progress or []
            ],
            "power_state": self.power_state,
            "power_state_control_progress": self.power_state_control_progress,
            "power_state_reinforcement": self.power_state_reinforcement,
            "power_state_undermining": self.power_state_undermining,
            "powers": self.powers,
            "thargoid_war": self.thargoid_war.to_sqlalchemy_dict() if self.thargoid_war is not None else None,
            # "timestamps": (self.timestamps.to_core_model() if self.timestamps is not None else None),
        }
