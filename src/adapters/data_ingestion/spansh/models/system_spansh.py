from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from src.adapters.data_ingestion.spansh.models.body_spansh import BodySpansh
from src.adapters.data_ingestion.spansh.models.common_spansh import (
    CoordinatesSpansh,
    TimestampsSpansh,
)
from src.adapters.data_ingestion.spansh.models.station_spansh import StationSpansh
from src.core.models.system_model import System


@dataclass_json
@dataclass
class FactionSpansh(DataClassJsonMixin):
    name: str
    influence: float

    government: Optional[str] = None
    allegiance: Optional[str] = None
    state: Optional[str] = None


@dataclass_json
@dataclass
class ControllingFactionSpansh(DataClassJsonMixin):
    allegiance: Optional[str] = None
    government: Optional[str] = None
    name: Optional[str] = None


@dataclass_json
@dataclass
class SystemSpansh(DataClassJsonMixin):
    allegiance: str
    bodies: List[BodySpansh]
    controlling_faction: ControllingFactionSpansh
    coords: CoordinatesSpansh
    date: datetime = field(
        metadata=config(
            decoder=datetime.fromisoformat,
            encoder=datetime.isoformat,
        )
    )
    factions: List[FactionSpansh]
    government: str
    id64: int
    name: str
    population: int
    primary_economy: str
    secondary_economy: str
    security: str
    stations: List[StationSpansh]

    body_count: Optional[int] = None

    controlling_power: Optional[str] = None
    power_conflict_progress: Optional[List[Any]] = None
    power_state: Optional[str] = None
    power_state_control_progress: Optional[float] = None
    power_state_reinforcement: Optional[float] = None
    power_state_undermining: Optional[float] = None
    powers: Optional[List[str]] = None

    thargoid_war: Optional[int] = None
    timestamps: Optional[TimestampsSpansh] = None

    def to_core_model(self) -> System:
        return System(
            allegiance=self.allegiance,
            bodies=self.bodies,
            controlling_faction=self.controlling_faction,
            coords=self.coords.to_core_model(),
            date=self.date,
            factions=self.factions,
            government=self.government,
            id64=self.id64,
            name=self.name,
            population=self.population,
            primary_economy=self.primary_economy,
            secondary_economy=self.secondary_economy,
            security=self.security,
            stations=self.stations,
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
