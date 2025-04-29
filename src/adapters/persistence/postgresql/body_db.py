from typing import Any, Dict, List, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.adapters.persistence.postgresql import BaseModel
from src.adapters.persistence.postgresql.system_db import SystemsDB


class BodiesDB(BaseModel):
    __tablename__ = "bodies"

    id: Mapped[int] = mapped_column(primary_key=True)
    id64: Mapped[int] = mapped_column(BigInteger, unique=True)
    spansh_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    edsm_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    body_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    system_id: Mapped[int] = mapped_column(ForeignKey("systems.id"))

    atmosphere_composition: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    materials: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    parents: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    absolute_magnitude: Mapped[Optional[float]] = mapped_column(Float)
    age: Mapped[Optional[int]] = mapped_column(Integer)
    arg_of_periapsis: Mapped[Optional[float]] = mapped_column(Float)
    ascending_Node: Mapped[Optional[float]] = mapped_column(Float)
    atmosphere_type: Mapped[Optional[str]] = mapped_column(Text)
    axial_tilt: Mapped[Optional[float]] = mapped_column(Float)
    distance_to_arrival: Mapped[Optional[float]] = mapped_column(Float)
    earth_masses: Mapped[Optional[float]] = mapped_column(Float)
    gravity: Mapped[Optional[float]] = mapped_column(Float)
    is_landable: Mapped[Optional[bool]] = mapped_column(Boolean)
    luminosity: Mapped[Optional[str]] = mapped_column(Text)
    main_star: Mapped[Optional[bool]] = mapped_column(Boolean)
    mean_anomaly: Mapped[Optional[float]] = mapped_column(Float)
    orbital_eccentricity: Mapped[Optional[float]] = mapped_column(Float)
    orbital_inclination: Mapped[Optional[float]] = mapped_column(Float)
    orbital_period: Mapped[Optional[float]] = mapped_column(Float)
    radius: Mapped[Optional[float]] = mapped_column(Float)
    reserve_level: Mapped[Optional[str]] = mapped_column(Text)
    rotational_period: Mapped[Optional[float]] = mapped_column(Float)
    rotational_period_tidally_locked: Mapped[Optional[bool]] = mapped_column(Boolean)
    semi_major_axis: Mapped[Optional[float]] = mapped_column(Float)
    solar_masses: Mapped[Optional[float]] = mapped_column(Float)
    solar_radius: Mapped[Optional[float]] = mapped_column(Float)
    solid_composition: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    spectral_class: Mapped[Optional[str]] = mapped_column(Text)
    sub_type: Mapped[Optional[str]] = mapped_column(Text)
    surface_pressure: Mapped[Optional[float]] = mapped_column(Float)
    surface_temperature: Mapped[Optional[float]] = mapped_column(Float)
    terraforming_state: Mapped[Optional[str]] = mapped_column(Text)
    type: Mapped[Optional[str]] = mapped_column(Text)
    volcanism_type: Mapped[Optional[str]] = mapped_column(Text)

    mean_anomaly_updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    distance_to_arrival_updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    system: Mapped["SystemsDB"] = relationship(back_populates="bodies")
    rings: Mapped[List["RingsDB"]] = relationship(back_populates="body")
    signals: Mapped[List["SignalsDB"]] = relationship(back_populates="body")

    def __repr__(self) -> str:
        return f"<BodiesDB(id={self.id}, name={self.name!r})>"


class SignalsDB(BaseModel):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(primary_key=True)
    body_id: Mapped[int] = mapped_column(ForeignKey("bodies.id"))
    signal_type: Mapped[Optional[str]] = mapped_column(Text)
    count: Mapped[Optional[int]] = mapped_column(Integer)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    body: Mapped["BodiesDB"] = relationship(back_populates="signals")

    def __repr__(self) -> str:
        return f"<SignalsDB(id={self.id}, signal_type={self.signal_type})>"


class RingsDB(BaseModel):
    __tablename__ = "rings"

    id: Mapped[int] = mapped_column(primary_key=True)
    body_id: Mapped[int] = mapped_column(ForeignKey("bodies.id"))
    id64: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[Optional[str]] = mapped_column(Text)
    mass: Mapped[Optional[float]] = mapped_column(Float)
    inner_radius: Mapped[Optional[float]] = mapped_column(Float)
    outer_radius: Mapped[Optional[float]] = mapped_column(Float)

    body: Mapped["BodiesDB"] = relationship(back_populates="rings")
    hotspots: Mapped[List["HotspotsDB"]] = relationship(back_populates="ring")

    def __repr__(self) -> str:
        return f"<RingsDB(id={self.id}, name={self.name})>"


class HotspotsDB(BaseModel):
    __tablename__ = "hotspots"

    id: Mapped[int] = mapped_column(primary_key=True)
    ring_id: Mapped[int] = mapped_column(ForeignKey("rings.id"))
    commodity_id: Mapped[int] = mapped_column(ForeignKey("commodities.id"))
    count: Mapped[Optional[int]] = mapped_column(Integer)

    ring: Mapped["RingsDB"] = relationship(back_populates="hotspots")

    def __repr__(self) -> str:
        return f"<HotspotsDB(id={self.id}, commodity_id={self.commodity_id})>"
