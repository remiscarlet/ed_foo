import math
from datetime import datetime

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
    controlling_power: datetime | None = None
    power_state: datetime | None = None
    powers: datetime | None = None
    distance_to_arrival: datetime | None = None
    mean_anomaly: datetime | None = None
