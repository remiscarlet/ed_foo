from datetime import datetime
from typing import Any, Tuple

from src.ingestion.spansh.models import BaseSpanshModel
from src.ingestion.spansh.models.common_spansh import TimestampsSpansh
from src.ingestion.spansh.models.station_spansh import StationSpansh


class SignalsSpansh(BaseSpanshModel):
    signals: dict[str, int]
    updated_at: datetime | None = None
    _validate_updated_at = BaseSpanshModel.flexible_datetime_validator("updated_at")

    def to_sqlalchemy_dicts(self, body_id: int) -> list[dict[str, Any]]:
        return [
            {
                "body_id": body_id,
                "signal_type": signal_type,
                "count": count,
                "updated_at": self.updated_at,
            }
            for signal_type, count in self.signals.items()
        ]

    def to_sqlalchemy_hotspot_dicts(self, ring_id: int) -> list[dict[str, Any]]:
        return [
            {
                "ring_id": ring_id,
                "commodity_sym": signal_type,
                "count": count,
                "updated_at": self.updated_at,
            }
            for signal_type, count in self.signals.items()
        ]


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

    def to_sqlalchemy_dict(self, body_id: int) -> dict[str, Any]:
        """Returns a RingsDB dict"""
        return {
            "body_id": body_id,
            "id64": self.id64,
            "name": self.name,
            "type": self.type,
            "mass": self.mass,
            "inner_radius": self.inner_radius,
            "outer_radius": self.outer_radius,
        }


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

    _validate_update_time = BaseSpanshModel.flexible_datetime_validator("update_time")

    def to_sqlalchemy_dict(self, system_id: int) -> dict[str, Any]:
        return {
            "system_id": system_id,
            "id64": self.id64,
            "body_id": self.body_id,
            "name": self.name,
            "absolute_magnitude": self.absolute_magnitude,
            "age": self.age,
            "arg_of_periapsis": self.arg_of_periapsis,
            "ascending_node": self.ascending_node,
            "atmosphere_composition": self.atmosphere_composition,
            "atmosphere_type": self.atmosphere_type,
            "axial_tilt": self.axial_tilt,
            "distance_to_arrival": self.distance_to_arrival,
            "earth_masses": self.earth_masses,
            "gravity": self.gravity,
            "is_landable": self.is_landable,
            "luminosity": self.luminosity,
            "main_star": self.main_star,
            "materials": self.materials,
            "mean_anomaly": self.mean_anomaly,
            "orbital_eccentricity": self.orbital_eccentricity,
            "orbital_inclination": self.orbital_inclination,
            "orbital_period": self.orbital_period,
            "parents": self.parents,
            "radius": self.radius,
            "reserve_level": self.reserve_level,
            "rotational_period": self.rotational_period,
            "rotational_period_tidally_locked": self.rotational_period_tidally_locked,
            "semi_major_axis": self.semi_major_axis,
            "solar_masses": self.solar_masses,
            "solar_radius": self.solar_radius,
            "solid_composition": self.solid_composition,
            "spectral_class": self.spectral_class,
            "sub_type": self.sub_type,
            "surface_pressure": self.surface_pressure,
            "surface_temperature": self.surface_temperature,
            "terraforming_state": self.terraforming_state,
            "type": self.type,
            "volcanism_type": self.volcanism_type,
            # "timestamps": self.timestamps.to_core_model() if self.timestamps is not None else None,
        }
