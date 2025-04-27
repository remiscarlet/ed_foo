from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from src.core.models.common_model import Timestamps
from src.core.models.station_model import Station


class HotSpots(BaseModel):
    hotspots: Dict[str, int]  # Commodity Name -> number
    updateTime: Optional[datetime] = None


class Signals(BaseModel):
    signals: Dict[str, int]
    updateTime: Optional[datetime] = None


class Asteroids(BaseModel):
    name: str
    type: str
    mass: float
    innerRadius: float
    outerRadius: float

    id64: Optional[int] = None
    signals: Optional[Signals] = None


class Body(BaseModel):
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
    belts: Optional[List[Asteroids]] = None
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
    rings: Optional[List[Asteroids]] = None
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

    def is_invalid_reserve_level(self, mineable: HasMineableMetadata) -> bool:
        if MiningMethod.CORE_MINING in mineable.mining_methods:
            return False
        elif MiningMethod.LASER_MINING in mineable.mining_methods:
            return self.reserveLevel != "Pristine"
        else:
            raise Exception(f"Got mineral with unknown mining method: '{mineable}'!")
