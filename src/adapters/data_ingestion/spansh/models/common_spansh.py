from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dataclasses_json import DataClassJsonMixin, dataclass_json


@dataclass_json
@dataclass
class CoordinatesSpansh(DataClassJsonMixin):
    x: float
    y: float
    z: float


@dataclass_json
@dataclass
class TimestampsSpansh(DataClassJsonMixin):
    controllingPower: Optional[datetime] = None
    powerState: Optional[datetime] = None
    powers: Optional[datetime] = None
    distanceToArrival: Optional[datetime] = None
    meanAnomaly: Optional[datetime] = None
