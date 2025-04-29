from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from dataclasses_json import DataClassJsonMixin, dataclass_json

from src.adapters.data_ingestion.spansh.models.common_spansh import TimestampsSpansh
from src.adapters.data_ingestion.spansh.models.station_spansh import StationSpansh


@dataclass_json
@dataclass
class SignalsSpansh:
    signals: Dict[str, int]
    updated_at: Optional[datetime] = None


@dataclass_json
@dataclass
class AsteroidsSpansh(DataClassJsonMixin):
    name: str
    type: str
    mass: float
    inner_radius: float
    outer_radius: float

    id64: Optional[int] = None
    signals: Optional[SignalsSpansh] = None


@dataclass_json
@dataclass
class BodySpansh(DataClassJsonMixin):
    id64: int
    bodyId: int
    name: str
    stations: List[StationSpansh]
    updated_at: datetime

    absolute_magnitude: Optional[float] = None
    age: Optional[int] = None
    arg_of_periapsis: Optional[float] = None
    ascending_node: Optional[float] = None
    atmosphere_composition: Optional[Dict[str, Any]] = None
    atmosphere_type: Optional[str] = None
    axial_tilt: Optional[float] = None
    belts: Optional[List[AsteroidsSpansh]] = None
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
    rings: Optional[List[AsteroidsSpansh]] = None
    rotational_period: Optional[float] = None
    rotational_period_tidally_locked: Optional[bool] = None
    semi_major_axis: Optional[float] = None
    signals: Optional[Dict[str, Any]] = None
    solar_masses: Optional[float] = None
    solar_radius: Optional[float] = None
    solid_composition: Optional[Any] = None
    spectral_class: Optional[str] = None
    sub_type: Optional[str] = None
    surface_pressure: Optional[float] = None
    surface_temperature: Optional[float] = None
    terraforming_state: Optional[str] = None
    timestamps: Optional[TimestampsSpansh] = None
    type: Optional[str] = None
    volcanism_type: Optional[str] = None
