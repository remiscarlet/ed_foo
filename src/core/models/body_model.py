from datetime import datetime
from typing import Any

from pydantic import BaseModel

from src.core.models.common_model import Timestamps
from src.core.models.station_model import Station


class HotSpots(BaseModel):
    hotspots: dict[str, int]  # Commodity Name -> number
    updated_at: datetime | None = None


class Signals(BaseModel):
    signals: dict[str, int]
    updated_at: datetime | None = None


class Asteroids(BaseModel):
    name: str
    type: str
    mass: float
    inner_radius: float
    outer_radius: float

    id64: int | None = None
    signals: Signals | None = None


class Body(BaseModel):
    name: str

    body_id: int | None = None
    id64: int | None = None
    stations: list[Station] | None = None
    absolute_magnitude: float | None = None
    age: int | None = None
    arg_of_periapsis: float | None = None
    ascending_node: float | None = None
    atmosphere_composition: dict[str, Any] | None = None
    atmosphere_type: str | None = None
    axial_tilt: float | None = None
    belts: list[Asteroids] | None = None
    distance_to_arrival: float | None = None
    earth_masses: float | None = None
    gravity: float | None = None
    is_landable: bool | None = None
    luminosity: str | None = None
    main_star: bool | None = None
    materials: dict[str, Any] | None = None
    mean_anomaly: float | None = None
    orbital_eccentricity: float | None = None
    orbital_inclination: float | None = None
    orbital_period: float | None = None
    parents: list[dict[str, int]] | None = None
    radius: float | None = None
    reserve_level: str | None = None
    rings: list[Asteroids] | None = None
    rotational_period: float | None = None
    rotational_period_tidally_locked: bool | None = None
    semi_major_axis: float | None = None
    signals: Signals | None = None
    solar_masses: float | None = None
    solar_radius: float | None = None
    solid_composition: Any | None = None
    spectral_class: str | None = None
    sub_type: str | None = None
    surface_pressure: float | None = None
    surface_temperature: float | None = None
    terraforming_state: str | None = None
    timestamps: Timestamps | None = None
    type: str | None = None
    volcanism_type: str | None = None

    mean_anomaly_updated_at: datetime | None = None
    distance_to_arrival_updated_at: datetime | None = None
