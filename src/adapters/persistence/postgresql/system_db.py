from typing import Any, Dict, List, Optional

from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.adapters.persistence.postgresql import BaseModel
from src.adapters.persistence.postgresql.body_db import BodiesDB
from src.adapters.persistence.postgresql.station_db import StationsDB


class FactionsDB(BaseModel):
    __tablename__ = "factions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullableo=False)

    allegiance: Mapped[Optional[str]] = mapped_column(Text)
    government: Mapped[Optional[str]] = mapped_column(Text)
    is_player: Mapped[Optional[bool]] = mapped_column(Boolean)

    faction_presences: Mapped[List["FactionPresencesDB"]] = relationship(back_populates="faction")

    def __repr__(self) -> str:
        return f"<FactionsDB(id={self.id}, name={self.name})>"


class FactionPresencesDB(BaseModel):
    __tablename__ = "faction_presences"

    id: Mapped[int] = mapped_column(primary_key=True)
    system_id: Mapped[int] = mapped_column(ForeignKey("systems.id"))
    faction_id: Mapped[int] = mapped_column(ForeignKey("factions.id"))

    influence: Mapped[Optional[float]] = mapped_column(Float)
    state: Mapped[Optional[str]] = mapped_column(Text)
    happiness: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    active_states: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    pending_states: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    recovering_states: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))

    system: Mapped["SystemsDB"] = relationship(back_populates="faction_presences")
    faction: Mapped["FactionsDB"] = relationship(back_populates="faction_presences")

    def __repr__(self) -> str:
        return f"<FactionPresencesDB(id={self.id}, system_id={self.system_id}, faction_id={self.faction_id})>"


class SystemsDB(BaseModel):
    __tablename__ = "systems"

    id: Mapped[int] = mapped_column(primary_key=True)
    id64: Mapped[int] = mapped_column(BigInteger, unique=True)
    spansh_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    edsm_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    allegiance: Mapped[Optional[str]] = mapped_column(Text)
    controlling_faction_id: Mapped[Optional[int]] = mapped_column(ForeignKey("factions.id"))
    x: Mapped[float] = mapped_column(Float)
    y: Mapped[float] = mapped_column(Float)
    z: Mapped[float] = mapped_column(Float)
    date: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    population: Mapped[Optional[int]] = mapped_column(Integer)
    primary_economy: Mapped[Optional[str]] = mapped_column(Text)
    secondary_economy: Mapped[Optional[str]] = mapped_column(Text)
    security: Mapped[Optional[str]] = mapped_column(Text)
    government: Mapped[Optional[str]] = mapped_column(Text)
    body_count: Mapped[Optional[int]] = mapped_column(Integer)
    controlling_power: Mapped[Optional[str]] = mapped_column(Text)
    power_conflict_progress: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    power_state: Mapped[Optional[str]] = mapped_column(Text)
    power_state_control_progress: Mapped[Optional[float]] = mapped_column(Float)
    power_state_reinforcement: Mapped[Optional[float]] = mapped_column(Float)
    power_state_undermining: Mapped[Optional[float]] = mapped_column(Float)
    powers: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    thargoid_war: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    controlling_power_updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    power_state_updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    powers_updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    bodies: Mapped[List["BodiesDB"]] = relationship(back_populates="system")
    stations: Mapped[List["StationsDB"]] = relationship(back_populates="system")
    faction_presences: Mapped[List["FactionPresencesDB"]] = relationship(back_populates="system")

    def __repr__(self) -> str:
        return f"<SystemsDB(id={self.id}, name={self.name!r})>"
