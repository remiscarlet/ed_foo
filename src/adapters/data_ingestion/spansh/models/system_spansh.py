from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from adapters.data_ingestion.spansh.models.body_spansh import BodySpansh
from adapters.data_ingestion.spansh.models.common_spansh import (
    CoordinatesSpansh,
    TimestampsSpansh,
)
from adapters.data_ingestion.spansh.models.station_spansh import StationSpansh
from src.core.models.system_model import System


@dataclass_json
@dataclass
class PlayerMinorFactionSpansh(DataClassJsonMixin):
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
    controllingFaction: ControllingFactionSpansh
    coords: CoordinatesSpansh
    date: datetime = field(
        metadata=config(
            decoder=datetime.fromisoformat,
            encoder=datetime.isoformat,
        )
    )
    factions: List[PlayerMinorFactionSpansh]
    government: str
    id64: int
    name: str
    population: int
    primaryEconomy: str
    secondaryEconomy: str
    security: str
    stations: List[StationSpansh]

    bodyCount: Optional[int] = None

    controllingPower: Optional[str] = None
    powerConflictProgress: Optional[List[Any]] = None
    powerState: Optional[str] = None
    powerStateControlProgress: Optional[float] = None
    powerStateReinforcement: Optional[float] = None
    powerStateUndermining: Optional[float] = None
    powers: Optional[List[str]] = None

    thargoidWar: Optional[int] = None
    timestamps: Optional[TimestampsSpansh] = None

    def to_core_system(self) -> System:
        return System(
            allegiance=self.allegiance,
            bodies=self.bodies,
            controllingFaction=self.controllingFaction,
            coords=self.coords,
            date=self.date,
            factions=self.factions,
            government=self.government,
            id64=self.id64,
            name=self.name,
            population=self.population,
            primaryEconomy=self.primaryEconomy,
            secondaryEconomy=self.secondaryEconomy,
            security=self.security,
            stations=self.stations,
            bodyCount=self.bodyCount,
            controllingPower=self.controllingPower,
            powerConflictProgress=self.powerConflictProgress,
            powerState=self.powerState,
            powerStateControlProgress=self.powerStateControlProgress,
            powerStateReinforcement=self.powerStateReinforcement,
            powerStateUndermining=self.powerStateUndermining,
            powers=self.powers,
            thargoidWar=self.thargoidWar,
            timestamps=self.timestamps,
        )
