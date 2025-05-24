from datetime import datetime
from typing import Any, Tuple

from ekaine.ingestion.spansh.models import BaseSpanshModel
from ekaine.ingestion.spansh.models.common_spansh import TimestampsSpansh
from ekaine.ingestion.spansh.models.station_spansh import StationSpansh


class SignalsSpansh(BaseSpanshModel):
    signals: dict[str, int]
    updated_at: datetime | None = None
    _validate_updated_at = BaseSpanshModel.flexible_datetime_validator("updated_at")


class AsteroidsSpansh(BaseSpanshModel):
    name: str
    type: str
    mass: float
    inner_radius: float
    outer_radius: float

    id64: int | None = None
    signals: SignalsSpansh | None = None

    def to_cache_key_tuple(self, spansh_body_id: int) -> Tuple[Any, ...]:
        return ("RingsDB", spansh_body_id, self.name)


class BodySpansh(BaseSpanshModel):
    def to_cache_key_tuple(self, system_id: int) -> Tuple[Any, ...]:
        return ("BodiesDB", system_id, self.name, self.body_id)

    def __repr__(self) -> str:
        return (
            f"BodySpansh(id64: {self.id64}, name: {self.name}, body_id: {self.body_id}, "
            f"type: {self.type}, sub_type: {self.sub_type}, main_star: {self.main_star})"
        )

    id64: int
    body_id: int
    name: str
    stations: list[StationSpansh]
    update_time: datetime | None = None
    _validate_updated_time = BaseSpanshModel.flexible_datetime_validator("update_time")

    absolute_magnitude: float | None = None
    age: int | None = None
    arg_of_periapsis: float | None = None
    ascending_node: float | None = None
    atmosphere_composition: dict[str, float] | None = None
    atmosphere_type: str | None = None
    axial_tilt: float | None = None
    belts: list[AsteroidsSpansh] | None = None
    distance_to_arrival: float | None = None
    earth_masses: float | None = None
    gravity: float | None = None
    is_landable: bool | None = None
    luminosity: str | None = None
    main_star: bool | None = None
    materials: dict[str, float] | None = None
    mean_anomaly: float | None = None
    orbital_eccentricity: float | None = None
    orbital_inclination: float | None = None
    orbital_period: float | None = None
    parents: list[dict[str, int]] | None = None
    radius: float | None = None
    reserve_level: str | None = None
    rings: list[AsteroidsSpansh] | None = None
    rotational_period: float | None = None
    rotational_period_tidally_locked: bool | None = None
    semi_major_axis: float | None = None
    signals: SignalsSpansh | None = None
    solar_masses: float | None = None
    solar_radius: float | None = None
    solid_composition: dict[str, float] | None = None
    spectral_class: str | None = None
    sub_type: str | None = None
    surface_pressure: float | None = None
    surface_temperature: float | None = None
    terraforming_state: str | None = None
    timestamps: TimestampsSpansh | None = None
    type: str | None = None
    volcanism_type: str | None = None
