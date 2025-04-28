from sqlalchemy import ARRAY, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.adapters.persistence.postgresql import BaseModel, HasCoordinates


class SignalsDB(BaseModel):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True)
    body_id = Column(Integer, ForeignKey("bodies.id"), nullable=False)
    signal_type = Column(String, nullable=False)
    count = Column(Integer)


class RingsDB(BaseModel):
    __tablename__ = "rings"

    id = Column(Integer, primary_key=True)
    body_id = Column(Integer, ForeignKey("bodies.id"), nullable=False)
    name = Column(String, nullable=False)

    hotspots = relationship("HotspotsDB", back_populates="ring")


class HotSpotsDB(BaseModel):
    __tablename__ = "hotspots"

    id = Column(Integer, primary_key=True)
    ring_id = Column(Integer, ForeignKey("rings.id"), nullable=False)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False)

    count = Column(Integer)

    ring = relationship("RingsDB", back_populates="hotspots")
    commodity = relationship("CommoditiesDB", back_populates="hotspots")


class FactionsDB(BaseModel):
    __tablename__ = "factions"
    id = Column(Integer, primary_key=True, index=True)
    system = relationship("SystemsDB", back_populates="factions")

    name = Column(String, index=True)
    influence = Column(Float)
    government = Column(String)
    allegiance = Column(String)
    state = Column(String)


class FactionPresencesDB(BaseModel):
    __tablename__ = "faction_presences"

    id = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey("systems.id64"), nullable=False)
    faction_id = Column(Integer, ForeignKey("factions.id"), nullable=False)

    influence = Column(Float)

    system = relationship("SystemsDB", back_populates="factions")
    faction = relationship("FactionsDB", back_populates="presences")


class SystemsDB(HasCoordinates):
    __tablename__ = "systems"

    id64 = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    date = Column(DateTime)

    population = Column(Integer, nullable=False)
    primaryEconomy = Column(String)
    secondaryEconomy = Column(String)
    security = Column(String)
    allegiance = Column(String)
    government = Column(String)

    bodies = relationship("BodiesDB", back_populates="system", cascade="all, delete-orphan")
    stations = relationship("StationsDB", back_populates="system", cascade="all, delete-orphan")
    factions = relationship("FactionsDB", back_populates="system", cascade="all, delete-orphan")
    controlling_faction_id = Column(Integer, ForeignKey("factions.id"), nullable=True)

    controllingPower = Column(String)
    powerConflictProgress = Column(JSONB)
    powerState = Column(String)
    powerStateControlProgress = Column(Float)
    powerStateReinforcement = Column(Float)
    powerStateUndermining = Column(Float)
    powers = Column(ARRAY(String))  # TODO: GIN Index

    thargoidWar = Column(JSONB)
