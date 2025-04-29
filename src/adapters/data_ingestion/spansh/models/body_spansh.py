from datetime import datetime
from typing import Any, Dict, List, Optional

from src.adapters.data_ingestion.spansh.models import BaseSpanshModel
from src.adapters.data_ingestion.spansh.models.common_spansh import TimestampsSpansh
from src.adapters.data_ingestion.spansh.models.station_spansh import StationSpansh
from src.core.models.body_model import Asteroids, Body, Signals
from src.core.ports.converter_port import ToCoreModel


class SignalsSpansh(BaseSpanshModel, ToCoreModel[Signals]):
    signals: Dict[str, int]
    updated_at: Optional[datetime] = None
    _validate_updated_at = BaseSpanshModel.flexible_datetime_validator("updated_at")

    def to_core_model(self) -> Signals:
        return Signals(
            signals=self.signals,
            updated_at=self.updated_at,
        )


class AsteroidsSpansh(BaseSpanshModel, ToCoreModel[Asteroids]):
    name: str
    type: str
    mass: float
    inner_radius: float
    outer_radius: float

    id64: Optional[int] = None
    signals: Optional[SignalsSpansh] = None

    def to_core_model(self) -> Asteroids:
        return Asteroids(
            name=self.name,
            type=self.type,
            mass=self.mass,
            inner_radius=self.inner_radius,
            outer_radius=self.outer_radius,
            id64=self.id64,
            signals=self.signals.to_core_model() if self.signals is not None else None,
        )


class BodySpansh(BaseSpanshModel, ToCoreModel[Body]):
    id64: int
    body_id: int
    name: str
    stations: List[StationSpansh]
    update_time: Optional[datetime] = None
    _validate_updated_time = BaseSpanshModel.flexible_datetime_validator("update_time")

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
    signals: Optional[SignalsSpansh] = None
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

    _validate_update_time = BaseSpanshModel.flexible_datetime_validator("update_time")

    def to_core_model(self) -> Body:
        return Body(
            id64=self.id64,
            body_id=self.body_id,
            name=self.name,
            stations=[station.to_core_model() for station in self.stations or []],
            updated_at=self.update_time,  # Rename
            absolute_magnitude=self.absolute_magnitude,
            age=self.age,
            arg_of_periapsis=self.arg_of_periapsis,
            ascending_node=self.ascending_node,
            atmosphere_composition=self.atmosphere_composition,
            atmosphere_type=self.atmosphere_type,
            axial_tilt=self.axial_tilt,
            belts=[belt.to_core_model() for belt in self.belts or []],
            distance_to_arrival=self.distance_to_arrival,
            earth_masses=self.earth_masses,
            gravity=self.gravity,
            is_landable=self.is_landable,
            luminosity=self.luminosity,
            main_star=self.main_star,
            materials=self.materials,
            mean_anomaly=self.mean_anomaly,
            orbital_eccentricity=self.orbital_eccentricity,
            orbital_inclination=self.orbital_inclination,
            orbital_period=self.orbital_period,
            parents=self.parents,
            radius=self.radius,
            reserve_level=self.reserve_level,
            rings=[ring.to_core_model() for ring in self.rings or []],
            rotational_period=self.rotational_period,
            rotational_period_tidally_locked=self.rotational_period_tidally_locked,
            semi_major_axis=self.semi_major_axis,
            signals=self.signals.to_core_model() if self.signals is not None else None,
            solar_masses=self.solar_masses,
            solar_radius=self.solar_radius,
            solid_composition=self.solid_composition,
            spectral_class=self.spectral_class,
            sub_type=self.sub_type,
            surface_pressure=self.surface_pressure,
            surface_temperature=self.surface_temperature,
            terraforming_state=self.terraforming_state,
            timestamps=self.timestamps.to_core_model() if self.timestamps is not None else None,
            type=self.type,
            volcanism_type=self.volcanism_type,
        )
