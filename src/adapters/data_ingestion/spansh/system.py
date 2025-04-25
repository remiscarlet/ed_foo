from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from dataclasses_json import DataClassJsonMixin, config, dataclass_json
from src.types import (
    Coordinates,
    MineableSymbols,
    Station,
    Timestamps,
)


@dataclass_json
@dataclass
class PlayerMinorFactionDTO(DataClassJsonMixin):
    name: str
    influence: float

    government: Optional[str] = None
    allegiance: Optional[str] = None
    state: Optional[str] = None


@dataclass_json
@dataclass
class ControllingFactionDTO(DataClassJsonMixin):
    allegiance: Optional[str] = None
    government: Optional[str] = None
    name: Optional[str] = None


@dataclass_json
@dataclass
class SignalsDTO:
    signals: Dict[MineableSymbols, int]
    updateTime: Optional[datetime] = None


@dataclass_json
@dataclass
class AsteroidsDTO(DataClassJsonMixin):
    name: str
    type: str
    mass: float
    innerRadius: float
    outerRadius: float

    id64: Optional[int] = None
    signals: Optional[SignalsDTO] = None


@dataclass_json
@dataclass
class BodyDTO(DataClassJsonMixin):
    id64: int
    bodyId: int
    name: str
    stations: List[Station]
    updateTime: datetime

    absoluteMagnitude: Optional[float] = None
    age: Optional[int] = None
    argOfPeriapsis: Optional[float] = None
    ascendingNode: Optional[float] = None
    atmosphereComposition: Optional[Dict[str, Any]] = None
    atmosphereType: Optional[str] = None
    axialTilt: Optional[float] = None
    belts: Optional[List[AsteroidsDTO]] = None
    distanceToArrival: Optional[float] = None
    earthMasses: Optional[float] = None
    gravity: Optional[float] = None
    isLandable: Optional[bool] = None
    luminosity: Optional[str] = None
    mainStar: Optional[bool] = None
    materials: Optional[Dict[str, Any]] = None
    meanAnomaly: Optional[float] = None
    orbitalEccentricity: Optional[float] = None
    orbitalInclination: Optional[float] = None
    orbitalPeriod: Optional[float] = None
    parents: Optional[List[Dict[str, int]]] = None
    radius: Optional[float] = None
    reserveLevel: Optional[str] = None
    rings: Optional[List[AsteroidsDTO]] = None
    rotationalPeriod: Optional[float] = None
    rotationalPeriodTidallyLocked: Optional[bool] = None
    semiMajorAxis: Optional[float] = None
    signals: Optional[Dict[str, Any]] = None
    solarMasses: Optional[float] = None
    solarRadius: Optional[float] = None
    solidComposition: Optional[Any] = None
    spectralClass: Optional[str] = None
    subType: Optional[str] = None
    surfacePressure: Optional[float] = None
    surfaceTemperature: Optional[float] = None
    terraformingState: Optional[str] = None
    timestamps: Optional[Timestamps] = None
    type: Optional[str] = None
    volcanismType: Optional[str] = None


@dataclass_json
@dataclass
class SystemDTO(DataClassJsonMixin):
    allegiance: str
    bodies: List[BodyDTO]
    controllingFaction: ControllingFactionDTO
    coords: Coordinates
    date: datetime = field(
        metadata=config(
            decoder=datetime.fromisoformat,
            encoder=datetime.isoformat,
        )
    )
    factions: List[PlayerMinorFactionDTO]
    government: str
    id64: int
    name: str
    population: int
    primaryEconomy: str
    secondaryEconomy: str
    security: str
    stations: List[Station]

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
