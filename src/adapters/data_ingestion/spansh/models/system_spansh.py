from datetime import datetime
from typing import Any, Dict, List, Optional

from src.adapters.data_ingestion.spansh.models import BaseSpanshModel
from src.adapters.data_ingestion.spansh.models.body_spansh import BodySpansh
from src.adapters.data_ingestion.spansh.models.common_spansh import (
    CoordinatesSpansh,
    TimestampsSpansh,
)
from src.adapters.data_ingestion.spansh.models.station_spansh import StationSpansh
from src.core.models.system_model import Faction, System
from src.core.ports.converter_port import ToCoreModel


class FactionSpansh(BaseSpanshModel, ToCoreModel[Faction]):
    name: str
    influence: Optional[float]

    government: Optional[str] = None
    allegiance: Optional[str] = None
    state: Optional[str] = None

    def to_core_model(self) -> Faction:
        return Faction(
            name=self.name,
            allegiance=self.allegiance,
            government=self.government,
            influence=self.influence,
            state=self.state,
        )


class ControllingFactionSpansh(BaseSpanshModel, ToCoreModel[Faction]):
    name: str
    allegiance: Optional[str] = None
    government: Optional[str] = None

    def to_core_model(self) -> Faction:
        return Faction(
            name=self.name,
            allegiance=self.allegiance,
            government=self.government,
        )


class SystemSpansh(BaseSpanshModel, ToCoreModel[System]):
    id64: int
    name: str

    allegiance: str
    controlling_faction: ControllingFactionSpansh
    coords: CoordinatesSpansh
    date: datetime
    _validate_date = BaseSpanshModel.flexible_datetime_validator("date")

    government: Optional[str] = None
    population: Optional[int] = None
    primary_economy: Optional[str] = None
    secondary_economy: Optional[str] = None
    security: Optional[str] = None

    bodies: Optional[List[BodySpansh]] = None
    factions: Optional[List[FactionSpansh]] = None
    stations: Optional[List[StationSpansh]] = None

    body_count: Optional[int] = None

    controlling_power: Optional[str] = None
    power_conflict_progress: Optional[List[Any]] = None
    power_state: Optional[str] = None
    power_state_control_progress: Optional[float] = None
    power_state_reinforcement: Optional[float] = None
    power_state_undermining: Optional[float] = None
    powers: Optional[List[str]] = None

    thargoid_war: Optional[Dict[str, Any]] = None
    timestamps: Optional[TimestampsSpansh] = None

    def to_core_model(self) -> System:
        return System(
            allegiance=self.allegiance,
            bodies=[body.to_core_model() for body in self.bodies or []],
            controlling_faction=self.controlling_faction.to_core_model(),
            coords=self.coords.to_core_model(),
            date=self.date,
            factions=[faction.to_core_model() for faction in self.factions or []],
            government=self.government,
            id64=self.id64,
            name=self.name,
            population=self.population,
            primary_economy=self.primary_economy,
            secondary_economy=self.secondary_economy,
            security=self.security,
            stations=[station.to_core_model() for station in self.stations or []],
            body_count=self.body_count,
            controlling_power=self.controlling_power,
            power_conflict_progress=self.power_conflict_progress,
            power_state=self.power_state,
            power_state_control_progress=self.power_state_control_progress,
            power_state_reinforcement=self.power_state_reinforcement,
            power_state_undermining=self.power_state_undermining,
            powers=self.powers,
            thargoid_war=self.thargoid_war,
            timestamps=(self.timestamps.to_core_model() if self.timestamps is not None else None),
        )
