from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dataclasses_json import DataClassJsonMixin, dataclass_json

from src.core.models.common_model import Coordinates, Timestamps


@dataclass_json
@dataclass
class CoordinatesSpansh(DataClassJsonMixin):
    x: float
    y: float
    z: float

    def to_core_model(self) -> Coordinates:
        return Coordinates(x=self.x, y=self.y, z=self.z)


@dataclass_json
@dataclass
class TimestampsSpansh(DataClassJsonMixin):
    controlling_power: Optional[datetime] = None
    power_state: Optional[datetime] = None
    powers: Optional[datetime] = None
    distance_to_arrival: Optional[datetime] = None
    mean_anomaly: Optional[datetime] = None

    def to_core_model(self) -> Timestamps:
        return Timestamps(
            controlling_power=self.controlling_power,
            power_state=self.power_state,
            powers=self.powers,
            distance_to_arrival=self.distance_to_arrival,
            mean_anomaly=self.mean_anomaly,
        )
