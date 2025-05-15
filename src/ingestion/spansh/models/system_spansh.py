from datetime import datetime
from typing import Any, Tuple

from pydantic import Field

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

    def to_sqlalchemy_dict(self) -> dict[str, Any]:
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
    influence: float | None

    government: str | None = None
    allegiance: str | None = None
    state: str | None = None

    def to_cache_key_tuple(self) -> Tuple[Any, ...]:
        return (self.__class__, self.name)

    def to_faction_sqlalchemy_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "allegiance": self.allegiance,
            "government": self.government,
        }

    def to_faction_presence_sqlalchemy_dict(self, system_id: int, faction_id: int) -> dict[str, Any]:
        return {
            "system_id": system_id,
            "faction_id": faction_id,
            "influence": self.influence,
            "state": self.state,
        }


class ControllingFactionSpansh(BaseSpanshModel):
    name: str
    allegiance: str | None = None
    government: str | None = None

    def to_cache_key_tuple(self) -> Tuple[Any, ...]:
        return (FactionSpansh, self.name)

    def to_sqlalchemy_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "allegiance": self.allegiance,
            "government": self.government,
        }


class PowerConflictProgressSpansh(BaseSpanshModel):
    power: str
    progress: float

    def to_sqlalchemy_dict(self) -> dict[str, Any]:
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

    controlling_faction: ControllingFactionSpansh | None
    government: str | None = None
    population: int | None = None
    primary_economy: str | None = None
    secondary_economy: str | None = None
    security: str | None = None

    bodies: list[BodySpansh] | None = None
    factions: list[FactionSpansh] | None = None
    all_stations: list[StationSpansh] | None = Field(alias="stations")

    body_count: int | None = None

    controlling_power: str | None = None
    power_conflict_progress: list[PowerConflictProgressSpansh] | None = None
    power_state: str | None = None
    power_state_control_progress: float | None = None
    power_state_reinforcement: float | None = None
    power_state_undermining: float | None = None
    powers: list[str] | None = None

    thargoid_war: ThargoidWarSpansh | None = None
    timestamps: TimestampsSpansh | None = None

    @property
    def stations(self) -> list[StationSpansh] | None:
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

        stations: list[StationSpansh] = []
        colonisation_ships: list[StationSpansh] = []
        for station in self.all_stations:
            if station.name == "System Colonisation Ship":
                colonisation_ships.append(station)
            else:
                stations.append(station)

        if colonisation_ships:
            newest_scs = max(
                colonisation_ships,
                key=lambda scs: (scs.update_time if scs.update_time is not None else datetime(year=1, month=1, day=1)),
            )
            stations.append(newest_scs)

        return stations

    def to_sqlalchemy_dict(self, controlling_faction_id: int | None) -> dict[str, Any]:
        return {
            "allegiance": self.allegiance,
            "controlling_faction_id": controlling_faction_id,
            "x": self.coords.x,
            "y": self.coords.y,
            "z": self.coords.z,
            "coords": self.coords.to_sqlalchemy_dict(),
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
            "controlling_power_updated_at": getattr(self.timestamps, "controlling_power", None),
            "power_state_updated_at": getattr(self.timestamps, "power_state", None),
            "powers_updated_at": getattr(self.timestamps, "powers", None),
        }
