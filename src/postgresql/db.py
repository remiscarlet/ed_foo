from datetime import datetime
from typing import Any, Optional, Tuple, Union

from geoalchemy2 import Geometry, WKBElement
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
    and_,
    literal,
    select,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, Session, foreign, mapped_column, relationship

from src.common.logging import get_logger
from src.postgresql import BaseModel, BaseModelWithId

logger = get_logger(__name__)


class BodiesDB(BaseModelWithId):
    unique_columns = ("system_id", "name", "body_id")
    __tablename__ = "bodies"
    __table_args__ = (
        UniqueConstraint(*unique_columns, name="_bodies_uc"),
        {"schema": "core"},
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)

    id64: Mapped[Optional[int]] = mapped_column(BigInteger)
    id_spansh: Mapped[Optional[int]] = mapped_column(BigInteger)
    id_edsm: Mapped[Optional[int]] = mapped_column(BigInteger)

    body_id: Mapped[Optional[int]] = mapped_column(Integer)  # The "idx" of the body _within the system_

    system_id: Mapped[int] = mapped_column(ForeignKey("core.systems.id"), nullable=False, index=True)
    system: Mapped["SystemsDB"] = relationship(back_populates="bodies")

    stations: Mapped[list["StationsDB"]] = relationship(
        "StationsDB",
        primaryjoin=lambda: and_(foreign(StationsDB.owner_id) == BodiesDB.id, StationsDB.owner_type == literal("body")),
        overlaps="stations",
    )

    atmosphere_composition: Mapped[Optional[dict[str, float]]] = mapped_column(JSONB)
    materials: Mapped[Optional[dict[str, float]]] = mapped_column(JSONB)
    parents: Mapped[Optional[dict[str, int]]] = mapped_column(JSONB)

    absolute_magnitude: Mapped[Optional[float]] = mapped_column(Float)
    age: Mapped[Optional[int]] = mapped_column(Integer)
    arg_of_periapsis: Mapped[Optional[float]] = mapped_column(Float)
    ascending_node: Mapped[Optional[float]] = mapped_column(Float)
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
    solid_composition: Mapped[Optional[dict[str, float]]] = mapped_column(JSONB)
    spectral_class: Mapped[Optional[str]] = mapped_column(Text)
    sub_type: Mapped[Optional[str]] = mapped_column(Text)
    surface_pressure: Mapped[Optional[float]] = mapped_column(Float)
    surface_temperature: Mapped[Optional[float]] = mapped_column(Float)
    terraforming_state: Mapped[Optional[str]] = mapped_column(Text)
    type: Mapped[Optional[str]] = mapped_column(Text)
    volcanism_type: Mapped[Optional[str]] = mapped_column(Text)

    mean_anomaly_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    distance_to_arrival_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    rings: Mapped[list["RingsDB"]] = relationship(back_populates="body")
    signals: Mapped[list["SignalsDB"]] = relationship(back_populates="body")

    def to_cache_key_tuple(self) -> Tuple[Any, ...]:
        return ("BodiesDB", self.system_id, self.name, self.body_id)

    def __repr__(self) -> str:
        return f"<BodiesDB(id={self.id}, name={self.name!r})>"


class SignalsDB(BaseModelWithId):
    unique_columns = ("body_id", "signal_type")
    __tablename__ = "signals"
    __table_args__ = (UniqueConstraint(*unique_columns, name="_signal_on_body_uc"), {"schema": "core"})

    body_id: Mapped[int] = mapped_column(ForeignKey("core.bodies.id"), nullable=False, index=True)
    body: Mapped["BodiesDB"] = relationship(back_populates="signals")

    signal_type: Mapped[Optional[str]] = mapped_column(Text)
    count: Mapped[Optional[int]] = mapped_column(Integer)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<SignalsDB(id={self.id}, signal_type={self.signal_type})>"


class RingsDB(BaseModelWithId):
    unique_columns = ("body_id", "name")
    __tablename__ = "rings"
    __table_args__ = (UniqueConstraint(*unique_columns, name="_ring_on_body_uc"), {"schema": "core"})

    id64: Mapped[int] = mapped_column(BigInteger, nullable=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    body_id: Mapped[int] = mapped_column(ForeignKey("core.bodies.id"), nullable=False, index=True)
    body: Mapped["BodiesDB"] = relationship(back_populates="rings")

    type: Mapped[Optional[str]] = mapped_column(Text)
    mass: Mapped[Optional[float]] = mapped_column(Float)
    inner_radius: Mapped[Optional[float]] = mapped_column(Float)
    outer_radius: Mapped[Optional[float]] = mapped_column(Float)

    hotspots: Mapped[list["HotspotsDB"]] = relationship(back_populates="ring")

    def to_cache_key_tuple(self) -> Tuple[Any, ...]:
        # String classname to work around circular imports from body_spansh.py
        return ("RingsDB", self.body_id, self.name)

    def __repr__(self) -> str:
        return f"<RingsDB(id={self.id}, name={self.name})>"


class HotspotsDB(BaseModelWithId):
    unique_columns = ("ring_id", "commodity_sym")
    __tablename__ = "hotspots"
    __table_args__ = (UniqueConstraint(*unique_columns, name="_ring_and_commodity_uc"), {"schema": "core"})

    ring_id: Mapped[int] = mapped_column(ForeignKey("core.rings.id"), nullable=False, index=True)
    ring: Mapped["RingsDB"] = relationship(back_populates="hotspots")
    commodity_sym: Mapped[str] = mapped_column(ForeignKey("core.commodities.symbol"))  # Small lookup table; no index

    count: Mapped[Optional[int]] = mapped_column(Integer)

    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<HotspotsDB(id={self.id}, commodity_sym={self.commodity_sym})>"


class StationsDB(BaseModelWithId):
    unique_columns = ("name", "owner_id")
    __tablename__ = "stations"
    __table_args__ = (UniqueConstraint(*unique_columns, name="_station_name_owner_distanace_uc"), {"schema": "core"})

    id64: Mapped[Optional[int]] = mapped_column(BigInteger)
    id_spansh: Mapped[Optional[int]] = mapped_column(BigInteger)
    id_edsm: Mapped[Optional[int]] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(Text, nullable=False, index=True)  # Station name is NOT unique

    owner_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    owner_type: Mapped[str] = mapped_column(Text, nullable=False, index=True)

    allegiance: Mapped[Optional[str]] = mapped_column(Text)
    controlling_faction: Mapped[Optional[str]] = mapped_column(Text)
    controlling_faction_state: Mapped[Optional[str]] = mapped_column(Text)
    distance_to_arrival: Mapped[Optional[float]] = mapped_column(Float)
    economies: Mapped[Optional[dict[str, float]]] = mapped_column(JSONB)
    government: Mapped[Optional[str]] = mapped_column(Text)

    large_landing_pads: Mapped[Optional[int]] = mapped_column(Integer)
    medium_landing_pads: Mapped[Optional[int]] = mapped_column(Integer)
    small_landing_pads: Mapped[Optional[int]] = mapped_column(Integer)

    primary_economy: Mapped[Optional[str]] = mapped_column(Text)
    services: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    type: Mapped[Optional[str]] = mapped_column(Text)

    # It kind of is a station-level detail...
    prohibited_commodities: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))

    carrier_name: Mapped[Optional[str]] = mapped_column(Text)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)

    spansh_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    edsm_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    eddn_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    def to_cache_key_tuple(self) -> Tuple[Any, ...]:
        tup = ("StationsDB", self.owner_id, self.name)
        logger.trace(f"STATIONSDB TO CACHE KEY TUPLE: {tup}")
        return tup

    def __repr__(self) -> str:
        return f"<StationsDB(id={self.id}, name={self.name!r})>"

    @property
    def parent(self) -> Union["SystemsDB", BodiesDB]:
        session = Session.object_session(self)
        if session is None:
            raise Exception("Could not find a valid Session attached to StationsDB object!")

        parent: Optional[SystemsDB | BodiesDB] = None
        if self.owner_type == "system":
            parent = session.execute(select(SystemsDB).where(SystemsDB.id == self.owner_id)).scalar_one_or_none()
        elif self.owner_type == "body":
            parent = session.execute(select(BodiesDB).where(BodiesDB.id == self.owner_id)).scalar_one_or_none()
        else:
            raise ValueError(f"Unknown owner_type: {self.owner_type}")

        if parent is None:
            raise Exception("Could not find a valid parent object!")

        return parent


class CommoditiesDB(BaseModel):
    unique_columns = ("symbol",)
    __tablename__ = "commodities"
    __table_args__ = {"schema": "core"}

    id64: Mapped[Optional[int]] = mapped_column(BigInteger)

    symbol: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    avg_price: Mapped[Optional[int]] = mapped_column(Integer)
    rare_goods: Mapped[Optional[bool]] = mapped_column(Boolean)
    corrosive: Mapped[Optional[bool]] = mapped_column(Boolean)

    category: Mapped[Optional[str]] = mapped_column(Text)
    is_mineable: Mapped[Optional[bool]] = mapped_column(Boolean)
    ring_types: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    mining_method: Mapped[Optional[str]] = mapped_column(Text)
    has_hotspots: Mapped[Optional[bool]] = mapped_column(Boolean)

    def __repr__(self) -> str:
        return f"<CommoditiesDB(id='{self.symbol}', name={self.name!r})>"


class MarketCommoditiesDB(BaseModelWithId):
    unique_columns = ("station_id", "commodity_sym")
    __tablename__ = "market_commodities"
    __table_args__ = (
        UniqueConstraint(*unique_columns, name="_station_market_commodity_uc"),
        {"schema": "core"},
    )

    station_id: Mapped[int] = mapped_column(Integer, ForeignKey("core.stations.id"), nullable=False, index=True)
    commodity_sym: Mapped[str] = mapped_column(Text, ForeignKey("core.commodities.symbol"), nullable=False)

    buy_price: Mapped[Optional[int]] = mapped_column(Integer)
    sell_price: Mapped[Optional[int]] = mapped_column(Integer)
    supply: Mapped[Optional[int]] = mapped_column(Integer)
    demand: Mapped[Optional[int]] = mapped_column(Integer)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<MarketCommoditiesDB(id={self.id}, station_id={self.station_id}, commodity_sym={self.commodity_sym})>"


class ShipsDB(BaseModel):
    __tablename__ = "ships"
    __table_args__ = {"schema": "core"}

    symbol: Mapped[str] = mapped_column(Text, primary_key=True)

    name: Mapped[Optional[str]] = mapped_column(Text)
    ship_id: Mapped[Optional[int]] = mapped_column(Integer)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<ShipsDB(symbol={self.symbol}, name={self.name})>"


class ShipyardShipsDB(BaseModelWithId):
    unique_columns = (
        "station_id",
        "ship_sym",
    )
    __tablename__ = "shipyard_ships"
    __table_args__ = (UniqueConstraint(*unique_columns, name="_station_shipyard_ship_uc"), {"schema": "core"})

    station_id: Mapped[int] = mapped_column(Integer, ForeignKey("core.stations.id"), nullable=False, index=True)
    ship_sym: Mapped[str] = mapped_column(
        Text, ForeignKey("core.ships.symbol"), nullable=False
    )  # Small lookup table; no index

    def __repr__(self) -> str:
        return f"<ShipyardShipsDB(id={self.id}, station_id={self.station_id}, ship_sym={self.ship_sym})>"


class ShipModulesDB(BaseModel):
    __tablename__ = "ship_modules"
    __table_args__ = {"schema": "core"}

    name: Mapped[str] = mapped_column(Text, primary_key=True)

    module_id: Mapped[Optional[int]] = mapped_column(Integer)
    symbol: Mapped[str] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(Text)
    rating: Mapped[Optional[str]] = mapped_column(Text)
    ship: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<ShipModulesDB(name={self.name})>"


class OutfittingShipModulesDB(BaseModelWithId):
    unique_columns = (
        "station_id",
        "module_name",
    )
    __tablename__ = "outfitting_ship_modules"
    __table_args__ = (UniqueConstraint(*unique_columns, name="_station_outfitting_module_uc"), {"schema": "core"})

    station_id: Mapped[int] = mapped_column(Integer, ForeignKey("core.stations.id"), nullable=False, index=True)
    module_name: Mapped[str] = mapped_column(
        Text, ForeignKey("core.ship_modules.name"), nullable=False
    )  # Small lookup table; no index
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<OutfittingShipModulesDB(id={self.id}, station_id={self.station_id}, module_name={self.module_name})>"


class ThargoidWarDB(BaseModelWithId):
    unique_columns = ("system_id",)
    __tablename__ = "thargoid_wars"
    __table_args__ = {"schema": "core"}

    system_id: Mapped[int] = mapped_column(Integer, ForeignKey("core.systems.id"), nullable=False, index=True)

    current_state: Mapped[str] = mapped_column(Text)
    days_remaining: Mapped[float] = mapped_column(Float)
    failure_state: Mapped[str] = mapped_column(Text)
    ports_remaining: Mapped[float] = mapped_column(Float)
    progress: Mapped[float] = mapped_column(Float)
    success_reached: Mapped[bool] = mapped_column(Boolean)
    success_state: Mapped[str] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<ThargoidWarDB(id={self.id}, system_id={self.system_id}, current_state={self.current_state})>"


class FactionsDB(BaseModelWithId):
    unique_columns = ("name",)
    __tablename__ = "factions"
    __table_args__ = {"schema": "core"}

    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    allegiance: Mapped[Optional[str]] = mapped_column(Text)
    government: Mapped[Optional[str]] = mapped_column(Text)
    is_player: Mapped[Optional[bool]] = mapped_column(Boolean)

    faction_presences: Mapped[list["FactionPresencesDB"]] = relationship(back_populates="faction")

    def __repr__(self) -> str:
        return f"<FactionsDB(id={self.id}, name={self.name})>"


class FactionPresencesDB(BaseModelWithId):
    unique_columns = ("system_id", "faction_id")
    __tablename__ = "faction_presences"
    __table_args__ = (
        UniqueConstraint(*unique_columns, name="_system_faction_presence_uc"),
        {"schema": "core"},
    )

    system_id: Mapped[int] = mapped_column(ForeignKey("core.systems.id"), nullable=False, index=True)
    system: Mapped["SystemsDB"] = relationship(back_populates="faction_presences")
    faction_id: Mapped[int] = mapped_column(ForeignKey("core.factions.id"), nullable=False, index=True)
    faction: Mapped["FactionsDB"] = relationship(back_populates="faction_presences")

    influence: Mapped[Optional[float]] = mapped_column(Float)
    state: Mapped[Optional[str]] = mapped_column(Text)
    happiness: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    active_states: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    pending_states: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    recovering_states: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))

    def __repr__(self) -> str:
        return f"<FactionPresencesDB(id={self.id}, system_id={self.system_id}, faction_id={self.faction_id})>"


class SystemsDB(BaseModelWithId):
    unique_columns = ("name",)
    __tablename__ = "systems"
    __table_args__ = {"schema": "core"}

    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    id64: Mapped[Optional[int]] = mapped_column(BigInteger)
    id_spansh: Mapped[Optional[int]] = mapped_column(BigInteger)
    id_edsm: Mapped[Optional[int]] = mapped_column(BigInteger)

    x: Mapped[float] = mapped_column(Float)
    y: Mapped[float] = mapped_column(Float)
    z: Mapped[float] = mapped_column(Float)
    coords: Mapped[WKBElement] = mapped_column(Geometry(geometry_type="POINTZ", srid=0))

    date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    allegiance: Mapped[Optional[str]] = mapped_column(Text)
    population: Mapped[Optional[int]] = mapped_column(BigInteger)
    primary_economy: Mapped[Optional[str]] = mapped_column(Text)
    secondary_economy: Mapped[Optional[str]] = mapped_column(Text)
    security: Mapped[Optional[str]] = mapped_column(Text)
    government: Mapped[Optional[str]] = mapped_column(Text)
    body_count: Mapped[Optional[int]] = mapped_column(Integer)
    controlling_power: Mapped[Optional[str]] = mapped_column(Text)
    power_conflict_progress: Mapped[Optional[list[dict[str, float]]]] = mapped_column(JSONB)
    power_state: Mapped[Optional[str]] = mapped_column(Text)
    power_state_control_progress: Mapped[Optional[float]] = mapped_column(Float)
    power_state_reinforcement: Mapped[Optional[float]] = mapped_column(Float)
    power_state_undermining: Mapped[Optional[float]] = mapped_column(Float)
    powers: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    thargoid_war: Mapped[Optional[dict[str, float]]] = mapped_column(JSONB)

    controlling_power_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    power_state_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    powers_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    controlling_faction_id: Mapped[Optional[int]] = mapped_column(ForeignKey("core.factions.id"), index=True)
    controlling_faction: Mapped[Optional["FactionsDB"]] = relationship()

    bodies: Mapped[list["BodiesDB"]] = relationship(back_populates="system")
    faction_presences: Mapped[list["FactionPresencesDB"]] = relationship(back_populates="system")
    stations: Mapped[list["StationsDB"]] = relationship(
        "StationsDB",
        primaryjoin=lambda: and_(
            foreign(StationsDB.owner_id) == SystemsDB.id, StationsDB.owner_type == literal("system")
        ),
        overlaps="stations",
    )

    def to_cache_key_tuple(self) -> Tuple[Any, ...]:
        return ("SystemsDB", self.name)

    def __repr__(self) -> str:
        return f"<SystemsDB(id={self.id}, name={self.name!r})>"
