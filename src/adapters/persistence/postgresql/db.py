from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    select,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from src.adapters.persistence.postgresql import BaseModel
from src.core.models.body_model import Body
from src.core.models.common_model import Coordinates
from src.core.models.system_model import Faction, System


class BodiesDB(BaseModel):
    __tablename__ = "bodies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    id64: Mapped[Optional[int]] = mapped_column(BigInteger)
    spansh_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    edsm_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    body_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    system_id: Mapped[int] = mapped_column(ForeignKey("systems.id"))
    system: Mapped["SystemsDB"] = relationship(back_populates="bodies")

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

    rings: Mapped[List["RingsDB"]] = relationship(back_populates="body")
    signals: Mapped[List["SignalsDB"]] = relationship(back_populates="body")

    @classmethod
    def from_core_model(cls, body: Body) -> "BodiesDB":
        return cls(
            id64=body.id64,
            name=body.name,
        )

    def to_core_model(self) -> Body:
        return Body(
            id64=self.id64,
            body_id=self.body_id,
            name=self.name,
        )

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
    ring: Mapped["RingsDB"] = relationship(back_populates="hotspots")
    commodity_sym: Mapped[str] = mapped_column(ForeignKey("commodities.symbol"))

    count: Mapped[Optional[int]] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"<HotspotsDB(id={self.id}, commodity_sym={self.commodity_sym})>"


class StationsDB(BaseModel):
    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(primary_key=True)
    id64: Mapped[Optional[int]] = mapped_column(BigInteger)
    spansh_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    edsm_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    system_id: Mapped[int] = mapped_column(ForeignKey("systems.id"))
    system: Mapped["SystemsDB"] = relationship(back_populates="stations")

    owner_id: Mapped[int] = mapped_column(nullable=False)
    owner_type: Mapped[str] = mapped_column(Text, nullable=False)

    allegiance: Mapped[Optional[str]] = mapped_column(Text)
    controlling_faction: Mapped[Optional[str]] = mapped_column(Text)
    controlling_faction_state: Mapped[Optional[str]] = mapped_column(Text)
    distance_to_arrival: Mapped[Optional[float]] = mapped_column(Float)
    economies: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    government: Mapped[Optional[str]] = mapped_column(Text)

    large_landing_pad: Mapped[Optional[int]] = mapped_column(Integer)
    medium_landing_pad: Mapped[Optional[int]] = mapped_column(Integer)
    small_landing_pad: Mapped[Optional[int]] = mapped_column(Integer)

    primary_economy: Mapped[Optional[str]] = mapped_column(Text)
    services: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    type: Mapped[Optional[str]] = mapped_column(Text)

    carrier_name: Mapped[Optional[str]] = mapped_column(Text)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)

    spansh_updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    edsm_updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    eddn_updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<StationsDB(id={self.id}, name={self.name!r})>"

    @property
    def parent(self) -> Union["SystemsDB", BodiesDB]:
        session = Session.object_session(self)
        if session is None:
            raise Exception("Could not find a valid Session attached to StationsDB object!")

        parent: Optional[Union[SystemsDB, BodiesDB]] = None
        if self.owner_type == "system":
            parent = session.scalars(select(SystemsDB).where(SystemsDB.id.is_(self.owner_id))).first()
        elif self.owner_type == "body":
            parent = session.scalars(select(BodiesDB).where(BodiesDB.id.is_(self.owner_id))).first()
        else:
            raise ValueError(f"Unknown owner_type: {self.owner_type}")

        if parent is None:
            raise Exception("Could not find a valid parent object!")

        return parent


class CommoditiesDB(BaseModel):
    __tablename__ = "commodities"

    symbol: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(Text)
    is_mineable: Mapped[Optional[bool]] = mapped_column(Boolean)
    ring_types: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    mining_method: Mapped[Optional[str]] = mapped_column(Text)
    has_hotspots: Mapped[Optional[bool]] = mapped_column(Boolean)

    def __repr__(self) -> str:
        return f"<CommoditiesDB(id='{self.symbol}', name={self.name!r})>"


class MarketCommoditiesDB(BaseModel):
    __tablename__ = "market_commodities"

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("stations.id"), nullable=False)
    commodity_sym: Mapped[str] = mapped_column(Text, ForeignKey("commodities.symbol"), nullable=False)

    buy_price: Mapped[Optional[int]] = mapped_column(Integer)
    sell_price: Mapped[Optional[int]] = mapped_column(Integer)
    stock: Mapped[Optional[int]] = mapped_column(BigInteger)
    demand: Mapped[Optional[int]] = mapped_column(BigInteger)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    is_blacklisted: Mapped[Optional[bool]] = mapped_column(Boolean)

    def __repr__(self) -> str:
        return f"<MarketCommoditiesDB(id={self.id}, station_id={self.station_id}, commodity_sym={self.commodity_sym})>"


class ShipsDB(BaseModel):
    __tablename__ = "ships"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[Optional[str]] = mapped_column(Text)
    name: Mapped[Optional[str]] = mapped_column(Text)
    ship_id: Mapped[Optional[int]] = mapped_column(Integer)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<ShipsDB(id={self.id}, name={self.name})>"


class ShipyardShipsDB(BaseModel):
    __tablename__ = "shipyard_ships"

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("stations.id"), nullable=False)
    ship_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("ships.id"), nullable=False)

    buy_price: Mapped[Optional[int]] = mapped_column(Integer)
    sell_price: Mapped[Optional[int]] = mapped_column(Integer)
    stock: Mapped[Optional[int]] = mapped_column(BigInteger)
    demand: Mapped[Optional[int]] = mapped_column(BigInteger)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    is_blacklisted: Mapped[Optional[bool]] = mapped_column(Boolean)

    def __repr__(self) -> str:
        return f"<ShipyardShipsDB(id={self.id}, station_id={self.station_id}, ship_id={self.ship_id})>"


class ShipModulesDB(BaseModel):
    __tablename__ = "ship_modules"

    id: Mapped[int] = mapped_column(primary_key=True)
    module_id: Mapped[Optional[int]] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    symbol: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(Text)
    rating: Mapped[Optional[str]] = mapped_column(Text)
    ship: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<ShipModulesDB(id={self.id}, name={self.name})>"


class OutfittingShipModulesDB(BaseModel):
    __tablename__ = "outfitting_ship_modules"

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("stations.id"), nullable=False)
    module_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("ship_modules.id"), nullable=False)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<OutfittingShipModulesDB(id={self.id}, station_id={self.station_id}, module_id={self.module_id})>"


class FactionsDB(BaseModel):
    __tablename__ = "factions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    allegiance: Mapped[Optional[str]] = mapped_column(Text)
    government: Mapped[Optional[str]] = mapped_column(Text)
    is_player: Mapped[Optional[bool]] = mapped_column(Boolean)

    faction_presences: Mapped[List["FactionPresencesDB"]] = relationship(back_populates="faction")

    @classmethod
    def from_core_model(cls, faction: Faction) -> "FactionsDB":
        return cls(
            name=faction.name,
            allegiance=faction.allegiance,
            government=faction.government,
        )

    def __repr__(self) -> str:
        return f"<FactionsDB(id={self.id}, name={self.name})>"


class FactionPresencesDB(BaseModel):
    __tablename__ = "faction_presences"
    __table_args__ = (UniqueConstraint("system_id", "faction_id", name="_system_faction_presence_uc"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    system_id: Mapped[int] = mapped_column(ForeignKey("systems.id"))
    system: Mapped["SystemsDB"] = relationship(back_populates="faction_presences")
    faction_id: Mapped[int] = mapped_column(ForeignKey("factions.id"))
    faction: Mapped["FactionsDB"] = relationship(back_populates="faction_presences")

    influence: Mapped[Optional[float]] = mapped_column(Float)
    state: Mapped[Optional[str]] = mapped_column(Text)
    happiness: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    active_states: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    pending_states: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    recovering_states: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))

    def __repr__(self) -> str:
        return f"<FactionPresencesDB(id={self.id}, system_id={self.system_id}, faction_id={self.faction_id})>"


class SystemsDB(BaseModel):
    __tablename__ = "systems"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True)

    id64: Mapped[Optional[int]] = mapped_column(BigInteger)
    spansh_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    edsm_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    x: Mapped[float] = mapped_column(Float)
    y: Mapped[float] = mapped_column(Float)
    z: Mapped[float] = mapped_column(Float)
    date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    allegiance: Mapped[Optional[str]] = mapped_column(Text)
    population: Mapped[Optional[int]] = mapped_column(BigInteger)
    primary_economy: Mapped[Optional[str]] = mapped_column(Text)
    secondary_economy: Mapped[Optional[str]] = mapped_column(Text)
    security: Mapped[Optional[str]] = mapped_column(Text)
    government: Mapped[Optional[str]] = mapped_column(Text)
    body_count: Mapped[Optional[int]] = mapped_column(Integer)
    controlling_power: Mapped[Optional[str]] = mapped_column(Text)
    power_conflict_progress: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB)
    power_state: Mapped[Optional[str]] = mapped_column(Text)
    power_state_control_progress: Mapped[Optional[float]] = mapped_column(Float)
    power_state_reinforcement: Mapped[Optional[float]] = mapped_column(Float)
    power_state_undermining: Mapped[Optional[float]] = mapped_column(Float)
    powers: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    thargoid_war: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    controlling_power_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    power_state_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    powers_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    controlling_faction_id: Mapped[Optional[int]] = mapped_column(ForeignKey("factions.id"))
    controlling_faction: Mapped[Optional["FactionsDB"]] = relationship()

    bodies: Mapped[List["BodiesDB"]] = relationship(back_populates="system")
    stations: Mapped[List["StationsDB"]] = relationship(back_populates="system")
    faction_presences: Mapped[List["FactionPresencesDB"]] = relationship(back_populates="system")

    @classmethod
    def from_core_model_to_dict(cls, system: System) -> Dict[str, Any]:
        return {
            "allegiance": system.allegiance,
            "bodies": [],  # [BodiesDB.from_core_model(body) for body in system.bodies],
            "controlling_faction": None,  # controlling_faction,
            "x": system.coords.x,
            "y": system.coords.y,
            "z": system.coords.z,
            "date": system.date,
            "government": system.government,
            "id64": system.id64,
            "name": system.name,
            "population": system.population,
            "primary_economy": system.primary_economy,
            "secondary_economy": system.secondary_economy,
            "security": system.security,
            "body_count": system.body_count,
            "controlling_power": system.controlling_power,
            "power_conflict_progress": system.power_conflict_progress,
            "power_state": system.power_state,
            "power_state_control_progress": system.power_state_control_progress,
            "power_state_reinforcement": system.power_state_reinforcement,
            "power_state_undermining": system.power_state_undermining,
            "powers": system.powers,
            "thargoid_war": system.thargoid_war,
        }

    def to_core_model(self) -> System:
        session = Session.object_session(self)
        if session is None:
            raise Exception("Could not find a valid Session attached to StationsDB object!")

        controlling_faction = None
        if self.controlling_faction_id is not None:
            controlling_faction = session.scalars(
                select(FactionsDB).where(FactionsDB.id.is_(self.controlling_faction_id))
            ).first()
            if controlling_faction is None:
                raise Exception("Associated controlling faction id could not be found in the FactionsDB!")

        factions = (
            session.query(FactionsDB)
            .join(FactionPresencesDB, FactionPresencesDB.faction_id == FactionsDB.id)
            .filter(FactionPresencesDB.system_id == self.id)
        ).all()

        return System(
            allegiance=self.allegiance,
            bodies=[body.to_core_model() for body in self.bodies],
            controlling_faction=controlling_faction.to_core_model() if controlling_faction is not None else None,
            coords=Coordinates(x=self.x, y=self.y, z=self.z),
            date=self.date,
            factions=[faction.to_core_model() for faction in factions],
            government=self.government,
            id64=self.id64,
            name=self.name,
            population=self.population,
            primary_economy=self.primary_economy,
            secondary_economy=self.secondary_economy,
            security=self.security,
            stations=[station.to_core_model() for station in self.stations],
            body_count=self.body_count,
            controlling_power=self.controlling_power,
            power_conflict_progress=self.power_conflict_progress,
            power_state=self.power_state,
            power_state_control_progress=self.power_state_control_progress,
            power_state_reinforcement=self.power_state_reinforcement,
            power_state_undermining=self.power_state_undermining,
            powers=self.powers,
            thargoid_war=self.thargoid_war,
        )

    def __repr__(self) -> str:
        return f"<SystemsDB(id={self.id}, name={self.name!r})>"
