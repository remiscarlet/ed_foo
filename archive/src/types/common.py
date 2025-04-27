import math
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dataclasses_json import DataClassJsonMixin, dataclass_json


@dataclass_json
@dataclass
class Coordinates(DataClassJsonMixin):
    x: float
    y: float
    z: float

    def distance_to(self, other: "Coordinates") -> float:
        dx = (self.x - other.x) ** 2
        dy = (self.y - other.y) ** 2
        dz = (self.z - other.z) ** 2
        return math.sqrt(dx + dy + dz)


@dataclass_json
@dataclass
class Timestamps(DataClassJsonMixin):
    controllingPower: Optional[datetime] = None
    powerState: Optional[datetime] = None
    powers: Optional[datetime] = None
    distanceToArrival: Optional[datetime] = None
    meanAnomaly: Optional[datetime] = None
