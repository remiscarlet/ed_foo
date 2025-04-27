import math
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Coordinates(BaseModel):
    x: float
    y: float
    z: float

    def distance_to(self, other: "Coordinates") -> float:
        dx = (self.x - other.x) ** 2
        dy = (self.y - other.y) ** 2
        dz = (self.z - other.z) ** 2
        return math.sqrt(dx + dy + dz)


class Timestamps(BaseModel):
    controllingPower: Optional[datetime] = None
    powerState: Optional[datetime] = None
    powers: Optional[datetime] = None
    distanceToArrival: Optional[datetime] = None
    meanAnomaly: Optional[datetime] = None
