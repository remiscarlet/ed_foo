from sqlalchemy import ARRAY, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.adapters.persistence.postgresql import BaseModel, HasCoordinates


class SignalDB(BaseModel):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True)
    body_id = Column(Integer, ForeignKey("body.id"), nullable=False)
    signal_type = Column(String, nullable=False)
    count = Column(Integer)


class RingDB(BaseModel):
    __tablename__ = "ring"

    id = Column(Integer, primary_key=True)
    body_id = Column(Integer, ForeignKey("body.id"), nullable=False)
    name = Column(String, nullable=False)

    hotspots = relationship("HotspotDB", back_populates="ring")


class HotSpotDB(BaseModel):
    __tablename__ = "hotspot"

    id = Column(Integer, primary_key=True)
    ring_id = Column(Integer, ForeignKey("ring.id"), nullable=False)
    commodity_id = Column(Integer, ForeignKey("commodity.id"), nullable=False)

    count = Column(Integer)

    ring = relationship("RingDB", back_populates="hotspots")
    commodity = relationship("CommodityDB", back_populates="hotspots")


class FactionDB(BaseModel):
    __tablename__ = "faction"
    id = Column(Integer, primary_key=True, index=True)
    system = relationship("SystemDB", back_populates="factions")

    name = Column(String, index=True)
    influence = Column(Float)
    government = Column(String)
    allegiance = Column(String)
    state = Column(String)


class FactionPresenceDB(BaseModel):
    __tablename__ = "faction_presences"

    id = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey("system.id64"), nullable=False)
    faction_id = Column(Integer, ForeignKey("faction.id"), nullable=False)

    influence = Column(Float)

    system = relationship("SystemDB", back_populates="factions")
    faction = relationship("FactionDB", back_populates="presences")


class SystemDB(HasCoordinates):
    __tablename__ = "system"

    id64 = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    date = Column(DateTime)

    population = Column(Integer, nullable=False)
    primaryEconomy = Column(String)
    secondaryEconomy = Column(String)
    security = Column(String)
    allegiance = Column(String)
    government = Column(String)

    bodies = relationship("BodyDB", back_populates="system", cascade="all, delete-orphan")
    stations = relationship("StationDB", back_populates="system", cascade="all, delete-orphan")
    factions = relationship("FactionDB", back_populates="system", cascade="all, delete-orphan")
    controlling_faction_id = Column(Integer, ForeignKey("faction.id"), nullable=True)

    controllingPower = Column(String)
    powerConflictProgress = Column(JSONB)
    powerState = Column(String)
    powerStateControlProgress = Column(Float)
    powerStateReinforcement = Column(Float)
    powerStateUndermining = Column(Float)
    powers = Column(ARRAY(String))  # TODO: GIN Index

    thargoidWar = Column(JSONB)
