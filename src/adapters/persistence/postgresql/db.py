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

from src.adapters.persistence.postgresql import BaseModel, BaseModelWithId
from src.common.logging import get_logger
from src.core.models.body_model import Body
from src.core.models.common_model import Coordinates
from src.core.models.station_model import Station
from src.core.models.system_model import Faction, System

logger = get_logger(__name__)


class BodiesDB(BaseModelWithId):
    __tablename__ = "bodies"
    __table_args__ = (
        UniqueConstraint("system_id", "name", "body_id", name="_bodies_uc"),
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

    def to_core_model(self) -> Body:
        return Body(
            body_id=self.body_id,
            name=self.name,
            id64=self.id64,
            stations=[station.to_core_model() for station in self.stations],
            absolute_magnitude=self.absolute_magnitude,
            age=self.age,
            arg_of_periapsis=self.arg_of_periapsis,
            ascending_node=self.ascending_node,
            atmosphere_type=self.atmosphere_type,
            axial_tilt=self.axial_tilt,
            distance_to_arrival=self.distance_to_arrival,
            earth_masses=self.earth_masses,
            gravity=self.gravity,
            is_landable=self.is_landable,
            luminosity=self.luminosity,
            main_star=self.main_star,
            mean_anomaly=self.mean_anomaly,
            orbital_eccentricity=self.orbital_eccentricity,
            orbital_inclination=self.orbital_inclination,
            orbital_period=self.orbital_period,
            radius=self.radius,
            reserve_level=self.reserve_level,
            rotational_period=self.rotational_period,
            rotational_period_tidally_locked=self.rotational_period_tidally_locked,
            semi_major_axis=self.semi_major_axis,
            solar_masses=self.solar_masses,
            solar_radius=self.solar_radius,
            solid_composition={k: float(v) for k, v in (self.solid_composition or {}).items()},
            spectral_class=self.spectral_class,
            sub_type=self.sub_type,
            surface_pressure=self.surface_pressure,
            surface_temperature=self.surface_temperature,
            terraforming_state=self.terraforming_state,
            type=self.type,
            volcanism_type=self.volcanism_type,
            mean_anomaly_updated_at=self.mean_anomaly_updated_at,
            distance_to_arrival_updated_at=self.distance_to_arrival_updated_at,
        )

    def to_cache_key_tuple(self) -> Tuple[Any, ...]:
        return ("BodiesDB", self.system_id, self.name, self.body_id)

    def __repr__(self) -> str:
        return f"<BodiesDB(id={self.id}, name={self.name!r})>"


class SignalsDB(BaseModelWithId):
    __tablename__ = "signals"
    __table_args__ = (UniqueConstraint("body_id", "signal_type", name="_signal_on_body_uc"), {"schema": "core"})

    body_id: Mapped[int] = mapped_column(ForeignKey("core.bodies.id"), nullable=False, index=True)
    body: Mapped["BodiesDB"] = relationship(back_populates="signals")

    signal_type: Mapped[Optional[str]] = mapped_column(Text)
    count: Mapped[Optional[int]] = mapped_column(Integer)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<SignalsDB(id={self.id}, signal_type={self.signal_type})>"


class RingsDB(BaseModelWithId):
    __tablename__ = "rings"
    __table_args__ = (UniqueConstraint("body_id", "name", name="_ring_on_body_uc"), {"schema": "core"})

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
    __tablename__ = "hotspots"
    __table_args__ = (UniqueConstraint("ring_id", "commodity_sym", name="_ring_and_commodity_uc"), {"schema": "core"})

    ring_id: Mapped[int] = mapped_column(ForeignKey("core.rings.id"), nullable=False, index=True)
    ring: Mapped["RingsDB"] = relationship(back_populates="hotspots")
    commodity_sym: Mapped[str] = mapped_column(ForeignKey("core.commodities.symbol"))  # Small lookup table; no index

    count: Mapped[Optional[int]] = mapped_column(Integer)

    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<HotspotsDB(id={self.id}, commodity_sym={self.commodity_sym})>"


class StationsDB(BaseModelWithId):
    __tablename__ = "stations"
    __table_args__ = (UniqueConstraint("name", "owner_id", name="_station_name_owner_distanace_uc"), {"schema": "core"})

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

    def to_core_model(self) -> Station:
        return Station(
            id64=self.id64,
            id_spansh=self.id_spansh,
            id_edsm=self.id_edsm,
            name=self.name,
            allegiance=self.allegiance,
            controlling_faction=self.controlling_faction,
            controlling_faction_state=self.controlling_faction_state,
            distance_to_arrival=self.distance_to_arrival,
            economies=self.economies,
            government=self.government,
            landing_pads={
                "large": self.large_landing_pads or 0,
                "medium": self.medium_landing_pads or 0,
                "small": self.small_landing_pads or 0,
            },
            primary_economy=self.primary_economy,
            services=self.services,
            type=self.type,
            carrier_name=self.carrier_name,
            latitude=self.latitude,
            longitude=self.longitude,
            spansh_updated_at=self.spansh_updated_at,
            edsm_updated_at=self.edsm_updated_at,
            eddn_updated_at=self.eddn_updated_at,
        )

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
    __tablename__ = "market_commodities"
    __table_args__ = (
        UniqueConstraint("station_id", "commodity_sym", name="_station_market_commodity_uc"),
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


class ShipsDB(BaseModelWithId):
    __tablename__ = "ships"
    __table_args__ = {"schema": "core"}

    symbol: Mapped[str] = mapped_column(Text)
    name: Mapped[Optional[str]] = mapped_column(Text)
    ship_id: Mapped[Optional[int]] = mapped_column(Integer)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<ShipsDB(id={self.id}, name={self.name})>"


class ShipyardShipsDB(BaseModelWithId):
    __tablename__ = "shipyard_ships"
    __table_args__ = {"schema": "core"}

    station_id: Mapped[int] = mapped_column(Integer, ForeignKey("core.stations.id"), nullable=False, index=True)
    ship_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("core.ships.id"), nullable=False
    )  # Small lookup table; no index

    def __repr__(self) -> str:
        return f"<ShipyardShipsDB(id={self.id}, station_id={self.station_id}, ship_id={self.ship_id})>"


class ShipModulesDB(BaseModelWithId):
    __tablename__ = "ship_modules"
    __table_args__ = {"schema": "core"}

    module_id: Mapped[Optional[int]] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    symbol: Mapped[str] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(Text)
    rating: Mapped[Optional[str]] = mapped_column(Text)
    ship: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<ShipModulesDB(id={self.id}, name={self.name})>"


class OutfittingShipModulesDB(BaseModelWithId):
    __tablename__ = "outfitting_ship_modules"
    __table_args__ = {"schema": "core"}

    station_id: Mapped[int] = mapped_column(Integer, ForeignKey("core.stations.id"), nullable=False, index=True)
    module_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("core.ship_modules.id"), nullable=False
    )  # Small lookup table; no index
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<OutfittingShipModulesDB(id={self.id}, station_id={self.station_id}, module_id={self.module_id})>"


class ThargoidWarDB(BaseModelWithId):
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
    __tablename__ = "factions"
    __table_args__ = {"schema": "core"}

    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    allegiance: Mapped[Optional[str]] = mapped_column(Text)
    government: Mapped[Optional[str]] = mapped_column(Text)
    is_player: Mapped[Optional[bool]] = mapped_column(Boolean)

    faction_presences: Mapped[list["FactionPresencesDB"]] = relationship(back_populates="faction")

    def to_core_model(self) -> Faction:
        return Faction(
            name=self.name,
            allegiance=self.allegiance,
            government=self.government,
            is_player=self.is_player,
        )

    def __repr__(self) -> str:
        return f"<FactionsDB(id={self.id}, name={self.name})>"


class FactionPresencesDB(BaseModelWithId):
    __tablename__ = "faction_presences"
    __table_args__ = (
        UniqueConstraint("system_id", "faction_id", name="_system_faction_presence_uc"),
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
    __tablename__ = "systems"
    __table_args__ = {"schema": "core"}

    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    id64: Mapped[Optional[int]] = mapped_column(BigInteger)
    id_spansh: Mapped[Optional[int]] = mapped_column(BigInteger)
    id_edsm: Mapped[Optional[int]] = mapped_column(BigInteger)

    x: Mapped[float] = mapped_column(Float)
    y: Mapped[float] = mapped_column(Float)
    z: Mapped[float] = mapped_column(Float)
    coords: Mapped[WKBElement] = mapped_column(Geometry(geometry_type="POINT", srid=0), nullable=True)

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

    @classmethod
    def from_core_model_to_dict(cls, system: System) -> dict[str, Any]:
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
