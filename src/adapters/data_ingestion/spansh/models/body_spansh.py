from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from dataclasses_json import DataClassJsonMixin, dataclass_json

from adapters.data_ingestion.spansh.models.common_spansh import TimestampsSpansh
from adapters.data_ingestion.spansh.models.station_spansh import StationSpansh


@dataclass_json
@dataclass
class SignalsSpansh:
    signals: Dict[str, int]
    updateTime: Optional[datetime] = None


@dataclass_json
@dataclass
class AsteroidsSpansh(DataClassJsonMixin):
    name: str
    type: str
    mass: float
    innerRadius: float
    outerRadius: float

    id64: Optional[int] = None
    signals: Optional[SignalsSpansh] = None


@dataclass_json
@dataclass
class BodySpansh(DataClassJsonMixin):
    id64: int
    bodyId: int
    name: str
    stations: List[StationSpansh]
    updateTime: datetime

    absoluteMagnitude: Optional[float] = None
    age: Optional[int] = None
    argOfPeriapsis: Optional[float] = None
    ascendingNode: Optional[float] = None
    atmosphereComposition: Optional[Dict[str, Any]] = None
    atmosphereType: Optional[str] = None
    axialTilt: Optional[float] = None
    belts: Optional[List[AsteroidsSpansh]] = None
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
    rings: Optional[List[AsteroidsSpansh]] = None
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
    timestamps: Optional[TimestampsSpansh] = None
    type: Optional[str] = None
    volcanismType: Optional[str] = None
