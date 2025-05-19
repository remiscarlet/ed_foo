from datetime import datetime

from geoalchemy2 import WKBElement
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from src.ingestion.spansh.models import BaseSpanshModel


class CoordinatesSpansh(BaseSpanshModel):
    x: float
    y: float
    z: float

    def to_sqlalchemy_dict(self) -> WKBElement:
        return from_shape(Point(self.x, self.y, self.z), srid=0)

    def __repr__(self) -> str:
        return f"CoordinatesSpansh(x={self.x}, y={self.y}, z={self.z})"


class TimestampsSpansh(BaseSpanshModel):
    controlling_power: datetime | None = None
    power_state: datetime | None = None
    powers: datetime | None = None
    distance_to_arrival: datetime | None = None
    mean_anomaly: datetime | None = None

    _validate_controlling_power = BaseSpanshModel.flexible_datetime_validator("controlling_power")
    _validate_power_state = BaseSpanshModel.flexible_datetime_validator("power_state")
    _validate_powers = BaseSpanshModel.flexible_datetime_validator("powers")
    _validate_distance_to_arrival = BaseSpanshModel.flexible_datetime_validator("distance_to_arrival")
    _validate_mean_anomaly = BaseSpanshModel.flexible_datetime_validator("mean_anomaly")
