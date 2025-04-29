from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from src.core.models.common_model import Timestamps
from src.core.models.station_model import Station


class HotSpots(BaseModel):
    hotspots: Dict[str, int]  # Commodity Name -> number
    updated_at: Optional[datetime] = None


class Signals(BaseModel):
    signals: Dict[str, int]
    updated_at: Optional[datetime] = None


class Asteroids(BaseModel):
    name: str
    type: str
    mass: float
    inner_radius: float
    outer_radius: float

    id64: Optional[int] = None
    signals: Optional[Signals] = None


class Body(BaseModel):
    id64: int
    body_id: int
    name: str

    stations: Optional[List[Station]] = None
    absolute_magnitude: Optional[float] = None
    age: Optional[int] = None
    arg_of_periapsis: Optional[float] = None
    ascending_node: Optional[float] = None
    atmosphere_composition: Optional[Dict[str, Any]] = None
    atmosphere_type: Optional[str] = None
    axial_tilt: Optional[float] = None
    belts: Optional[List[Asteroids]] = None
    distance_to_arrival: Optional[float] = None
    earth_masses: Optional[float] = None
    gravity: Optional[float] = None
    is_landable: Optional[bool] = None
    luminosity: Optional[str] = None
    main_star: Optional[bool] = None
    materials: Optional[Dict[str, Any]] = None
    mean_anomaly: Optional[float] = None
    orbital_eccentricity: Optional[float] = None
    orbital_inclination: Optional[float] = None
    orbital_period: Optional[float] = None
    parents: Optional[List[Dict[str, int]]] = None
    radius: Optional[float] = None
    reserve_level: Optional[str] = None
    rings: Optional[List[Asteroids]] = None
    rotational_period: Optional[float] = None
    rotational_period_tidally_locked: Optional[bool] = None
    semi_major_axis: Optional[float] = None
    signals: Optional[Signals] = None
    solar_masses: Optional[float] = None
    solar_radius: Optional[float] = None
    solid_composition: Optional[Any] = None
    spectral_class: Optional[str] = None
    sub_type: Optional[str] = None
    surface_pressure: Optional[float] = None
    surface_temperature: Optional[float] = None
    terraforming_state: Optional[str] = None
    timestamps: Optional[Timestamps] = None
    type: Optional[str] = None
    volcanism_type: Optional[str] = None

    mean_anomaly_updated_at: Optional[datetime] = None
    distance_to_arrival_updated_at: Optional[datetime] = None
