from datetime import datetime
from pprint import pformat
from typing import Any, Optional, Tuple, Union, cast

from gen.eddn_models import commodity_v3_0, journal_v1_0
from geoalchemy2 import Geometry, WKBElement
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    UniqueConstraint,
    and_,
    literal,
    select,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TEXT
from sqlalchemy.orm import Mapped, Session, foreign, mapped_column, relationship

from src.common.game_constants import get_symbol_by_eddn_name
from src.common.logging import get_logger
from src.ingestion.spansh.models.body_spansh import (
    AsteroidsSpansh,
    BodySpansh,
    SignalsSpansh,
)
from src.ingestion.spansh.models.common_spansh import CoordinatesSpansh
from src.ingestion.spansh.models.station_spansh import CommoditySpansh, StationSpansh
from src.ingestion.spansh.models.system_spansh import (
    ControllingFactionSpansh,
    FactionSpansh,
    PowerConflictProgressSpansh,
    SystemSpansh,
    ThargoidWarSpansh,
)
from src.postgresql import BaseModel, BaseModelWithId

logger = get_logger(__name__)


class BodiesDB(BaseModelWithId):
    unique_columns = ("system_id", "name", "body_id")
    __tablename__ = "bodies"
    __table_args__ = (
        UniqueConstraint(*unique_columns, name="_bodies_uc"),
        {"schema": "core"},
    )

    name: Mapped[str] = mapped_column(TEXT, nullable=False)

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
    atmosphere_type: Mapped[Optional[str]] = mapped_column(TEXT)
    axial_tilt: Mapped[Optional[float]] = mapped_column(Float)
    distance_to_arrival: Mapped[Optional[float]] = mapped_column(Float)
    earth_masses: Mapped[Optional[float]] = mapped_column(Float)
    gravity: Mapped[Optional[float]] = mapped_column(Float)
    is_landable: Mapped[Optional[bool]] = mapped_column(Boolean)
    luminosity: Mapped[Optional[str]] = mapped_column(TEXT)
    main_star: Mapped[Optional[bool]] = mapped_column(Boolean)
    mean_anomaly: Mapped[Optional[float]] = mapped_column(Float)
    orbital_eccentricity: Mapped[Optional[float]] = mapped_column(Float)
    orbital_inclination: Mapped[Optional[float]] = mapped_column(Float)
    orbital_period: Mapped[Optional[float]] = mapped_column(Float)
    radius: Mapped[Optional[float]] = mapped_column(Float)
    reserve_level: Mapped[Optional[str]] = mapped_column(TEXT)
    rotational_period: Mapped[Optional[float]] = mapped_column(Float)
    rotational_period_tidally_locked: Mapped[Optional[bool]] = mapped_column(Boolean)
    semi_major_axis: Mapped[Optional[float]] = mapped_column(Float)
    solar_masses: Mapped[Optional[float]] = mapped_column(Float)
    solar_radius: Mapped[Optional[float]] = mapped_column(Float)
    solid_composition: Mapped[Optional[dict[str, float]]] = mapped_column(JSONB)
    spectral_class: Mapped[Optional[str]] = mapped_column(TEXT)
    sub_type: Mapped[Optional[str]] = mapped_column(TEXT)
    surface_pressure: Mapped[Optional[float]] = mapped_column(Float)
    surface_temperature: Mapped[Optional[float]] = mapped_column(Float)
    terraforming_state: Mapped[Optional[str]] = mapped_column(TEXT)
    type: Mapped[Optional[str]] = mapped_column(TEXT)
    volcanism_type: Mapped[Optional[str]] = mapped_column(TEXT)

    mean_anomaly_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    distance_to_arrival_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    rings: Mapped[list["RingsDB"]] = relationship(back_populates="body")
    signals: Mapped[list["SignalsDB"]] = relationship(back_populates="body")

    def to_cache_key_tuple(self) -> Tuple[Any, ...]:
        return ("BodiesDB", self.system_id, self.name, self.body_id)

    @staticmethod
    def to_dict_from_spansh(spansh_body: BodySpansh, system_id: int) -> dict[str, Any]:
        return {
            "system_id": system_id,
            "id64": spansh_body.id64,
            "body_id": spansh_body.body_id,
            "name": spansh_body.name,
            "absolute_magnitude": spansh_body.absolute_magnitude,
            "age": spansh_body.age,
            "arg_of_periapsis": spansh_body.arg_of_periapsis,
            "ascending_node": spansh_body.ascending_node,
            "atmosphere_composition": spansh_body.atmosphere_composition,
            "atmosphere_type": spansh_body.atmosphere_type,
            "axial_tilt": spansh_body.axial_tilt,
            "distance_to_arrival": spansh_body.distance_to_arrival,
            "earth_masses": spansh_body.earth_masses,
            "gravity": spansh_body.gravity,
            "is_landable": spansh_body.is_landable,
            "luminosity": spansh_body.luminosity,
            "main_star": spansh_body.main_star,
            "materials": spansh_body.materials,
            "mean_anomaly": spansh_body.mean_anomaly,
            "orbital_eccentricity": spansh_body.orbital_eccentricity,
            "orbital_inclination": spansh_body.orbital_inclination,
            "orbital_period": spansh_body.orbital_period,
            "parents": spansh_body.parents,
            "radius": spansh_body.radius,
            "reserve_level": spansh_body.reserve_level,
            "rotational_period": spansh_body.rotational_period,
            "rotational_period_tidally_locked": spansh_body.rotational_period_tidally_locked,
            "semi_major_axis": spansh_body.semi_major_axis,
            "solar_masses": spansh_body.solar_masses,
            "solar_radius": spansh_body.solar_radius,
            "solid_composition": spansh_body.solid_composition,
            "spectral_class": spansh_body.spectral_class,
            "sub_type": spansh_body.sub_type,
            "surface_pressure": spansh_body.surface_pressure,
            "surface_temperature": spansh_body.surface_temperature,
            "terraforming_state": spansh_body.terraforming_state,
            "type": spansh_body.type,
            "volcanism_type": spansh_body.volcanism_type,
            "mean_anomaly_updated_at": getattr(spansh_body.timestamps, "mean_anomaly", None),
            "distance_to_arrival_updated_at": getattr(spansh_body.timestamps, "distance_to_arrival", None),
        }

    def __repr__(self) -> str:
        return f"<BodiesDB(id={self.id}, name={self.name!r})>"


class SignalsDB(BaseModelWithId):
    unique_columns = ("body_id", "signal_type")
    __tablename__ = "signals"
    __table_args__ = (UniqueConstraint(*unique_columns, name="_signal_on_body_uc"), {"schema": "core"})

    body_id: Mapped[int] = mapped_column(ForeignKey("core.bodies.id"), nullable=False, index=True)
    body: Mapped["BodiesDB"] = relationship(back_populates="signals")

    signal_type: Mapped[Optional[str]] = mapped_column(TEXT)
    count: Mapped[Optional[int]] = mapped_column(Integer)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    @staticmethod
    def to_dicts_from_spansh(spansh_signal: SignalsSpansh, body_id: int) -> list[dict[str, Any]]:
        return [
            {
                "body_id": body_id,
                "signal_type": signal_type,
                "count": count,
                "updated_at": spansh_signal.updated_at,
            }
            for signal_type, count in spansh_signal.signals.items()
        ]

    def __repr__(self) -> str:
        return f"<SignalsDB(id={self.id}, signal_type={self.signal_type})>"


class RingsDB(BaseModelWithId):
    unique_columns = ("body_id", "name")
    __tablename__ = "rings"
    __table_args__ = (UniqueConstraint(*unique_columns, name="_ring_on_body_uc"), {"schema": "core"})

    id64: Mapped[int] = mapped_column(BigInteger, nullable=True)
    name: Mapped[str] = mapped_column(TEXT, nullable=False)

    body_id: Mapped[int] = mapped_column(ForeignKey("core.bodies.id"), nullable=False, index=True)
    body: Mapped["BodiesDB"] = relationship(back_populates="rings")

    type: Mapped[Optional[str]] = mapped_column(TEXT)
    mass: Mapped[Optional[float]] = mapped_column(Float)
    inner_radius: Mapped[Optional[float]] = mapped_column(Float)
    outer_radius: Mapped[Optional[float]] = mapped_column(Float)

    hotspots: Mapped[list["HotspotsDB"]] = relationship(back_populates="ring")

    def to_cache_key_tuple(self) -> Tuple[Any, ...]:
        # String classname to work around circular imports from body_spansh.py
        return ("RingsDB", self.body_id, self.name)

    @staticmethod
    def to_dict_from_spansh(spansh_asteroid: AsteroidsSpansh, body_id: int) -> dict[str, Any]:
        """Returns a RingsDB dict"""
        return {
            "body_id": body_id,
            "id64": spansh_asteroid.id64,
            "name": spansh_asteroid.name,
            "type": spansh_asteroid.type,
            "mass": spansh_asteroid.mass,
            "inner_radius": spansh_asteroid.inner_radius,
            "outer_radius": spansh_asteroid.outer_radius,
        }

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

    @staticmethod
    def to_dicts_from_spansh(spansh_signal: SignalsSpansh, ring_id: int) -> list[dict[str, Any]]:
        return [
            {
                "ring_id": ring_id,
                "commodity_sym": signal_type,
                "count": count,
                "updated_at": spansh_signal.updated_at,
            }
            for signal_type, count in spansh_signal.signals.items()
        ]

    def __repr__(self) -> str:
        return f"<HotspotsDB(id={self.id}, commodity_sym={self.commodity_sym})>"


class StationsDB(BaseModelWithId):
    unique_columns = ("name", "owner_id")
    __tablename__ = "stations"
    __table_args__ = (UniqueConstraint(*unique_columns, name="_station_name_owner_distanace_uc"), {"schema": "core"})

    id64: Mapped[Optional[int]] = mapped_column(BigInteger)
    id_spansh: Mapped[Optional[int]] = mapped_column(BigInteger)
    id_edsm: Mapped[Optional[int]] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(TEXT, nullable=False, index=True)  # Station name is NOT unique

    owner_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    owner_type: Mapped[str] = mapped_column(TEXT, nullable=False, index=True)

    allegiance: Mapped[Optional[str]] = mapped_column(TEXT)
    controlling_faction: Mapped[Optional[str]] = mapped_column(TEXT)
    controlling_faction_state: Mapped[Optional[str]] = mapped_column(TEXT)
    distance_to_arrival: Mapped[Optional[float]] = mapped_column(Float)
    economies: Mapped[Optional[dict[str, float]]] = mapped_column(JSONB)
    government: Mapped[Optional[str]] = mapped_column(TEXT)

    large_landing_pads: Mapped[Optional[int]] = mapped_column(Integer)
    medium_landing_pads: Mapped[Optional[int]] = mapped_column(Integer)
    small_landing_pads: Mapped[Optional[int]] = mapped_column(Integer)

    primary_economy: Mapped[Optional[str]] = mapped_column(TEXT)
    services: Mapped[Optional[list[str]]] = mapped_column(ARRAY(TEXT))
    type: Mapped[Optional[str]] = mapped_column(TEXT)

    # It kind of is a station-level detail...
    prohibited_commodities: Mapped[Optional[list[str]]] = mapped_column(ARRAY(TEXT))

    carrier_name: Mapped[Optional[str]] = mapped_column(TEXT)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)

    spansh_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    edsm_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    eddn_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    def to_cache_key_tuple(self) -> Tuple[Any, ...]:
        tup = ("StationsDB", self.owner_id, self.name)
        logger.trace(f"STATIONSDB TO CACHE KEY TUPLE: {tup}")
        return tup

    @staticmethod
    def to_dict_from_spansh(spansh_station: StationSpansh, owner_id: int, owner_type: str) -> dict[str, Any]:
        if spansh_station.landing_pads is not None:
            large_pads = spansh_station.landing_pads.get("large", 0)
            medium_pads = spansh_station.landing_pads.get("medium", 0)
            small_pads = spansh_station.landing_pads.get("small", 0)
        else:
            large_pads = 0
            medium_pads = 0
            small_pads = 0
        return {
            "id_spansh": spansh_station.id,
            "owner_id": owner_id,
            "owner_type": owner_type,
            "name": spansh_station.name,
            "allegiance": spansh_station.allegiance,
            "controlling_faction": spansh_station.controlling_faction,
            "controlling_faction_state": spansh_station.controlling_faction_state,
            "distance_to_arrival": spansh_station.distance_to_arrival,
            "economies": spansh_station.economies,
            "government": spansh_station.government,
            "large_landing_pads": large_pads,
            "medium_landing_pads": medium_pads,
            "small_landing_pads": small_pads,
            "primary_economy": spansh_station.primary_economy,
            "prohibited_commodities": getattr(spansh_station.market, "prohibited_commodities", None),
            "services": spansh_station.services,
            "type": spansh_station.type,
            "carrier_name": spansh_station.carrier_name,
            "latitude": spansh_station.latitude,
            "longitude": spansh_station.longitude,
            "spansh_updated_at": spansh_station.update_time,
        }

    # @staticmethod
    # def to_dicts_from_eddn(eddn_model: approachsettlement_v1_0.Model, system_id: int) -> list[dict[str, Any]]:
    #     dicts = []
    #     for commodity in eddn_model.message:
    #         symbol = get_symbol_by_eddn_name(commodity.name)
    #         if symbol is None:
    #             logger.warning(
    #                 "Encountered a commodity in an EDDN Commodity model we didn't know about! "
    #                 f"Got: '{commodity.name}'"
    #             )
    #             continue

    #         dicts.append(
    #             {
    #                 "station_id": station_id,
    #                 "commodity_sym": symbol,
    #                 "buy_price": commodity.buyPrice,
    #                 "sell_price": commodity.sellPrice,
    #                 "supply": commodity.stock,
    #                 "demand": commodity.demand,
    #                 "updated_at": eddn_model.message.timestamp,
    #             }
    #         )
    #     return dicts

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

    symbol: Mapped[str] = mapped_column(TEXT, primary_key=True)
    name: Mapped[str] = mapped_column(TEXT, nullable=False)

    avg_price: Mapped[Optional[int]] = mapped_column(Integer)
    rare_goods: Mapped[Optional[bool]] = mapped_column(Boolean)
    corrosive: Mapped[Optional[bool]] = mapped_column(Boolean)

    category: Mapped[Optional[str]] = mapped_column(TEXT)
    is_mineable: Mapped[Optional[bool]] = mapped_column(Boolean)
    ring_types: Mapped[Optional[list[str]]] = mapped_column(ARRAY(TEXT))
    mining_method: Mapped[Optional[str]] = mapped_column(TEXT)
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
    commodity_sym: Mapped[str] = mapped_column(TEXT, ForeignKey("core.commodities.symbol"), nullable=False)

    buy_price: Mapped[Optional[int]] = mapped_column(Integer)
    sell_price: Mapped[Optional[int]] = mapped_column(Integer)
    supply: Mapped[Optional[int]] = mapped_column(Integer)
    demand: Mapped[Optional[int]] = mapped_column(Integer)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    @staticmethod
    def to_dict_from_spansh(
        spansh_commodity: CommoditySpansh, station_id: int, commodity_sym: str, market_updated_at: datetime | None
    ) -> dict[str, Any]:
        return {
            "station_id": station_id,
            "commodity_sym": commodity_sym,
            "buy_price": spansh_commodity.buy_price,
            "sell_price": spansh_commodity.sell_price,
            "supply": spansh_commodity.supply,
            "demand": spansh_commodity.demand,
            "updated_at": spansh_commodity.updated_at or market_updated_at,
        }

    @staticmethod
    def to_dicts_from_eddn(eddn_model: commodity_v3_0.Model, station_id: int) -> list[dict[str, Any]]:
        dicts = []
        for commodity in eddn_model.message.commodities:
            symbol = get_symbol_by_eddn_name(commodity.name)
            if symbol is None:
                logger.warning(
                    f"Encountered a commodity in an EDDN Commodity model we didn't know about! Got: '{commodity.name}'"
                )
                continue

            dicts.append(
                {
                    "station_id": station_id,
                    "commodity_sym": symbol,
                    "buy_price": commodity.buyPrice,
                    "sell_price": commodity.sellPrice,
                    "supply": commodity.stock,
                    "demand": commodity.demand,
                    "updated_at": eddn_model.message.timestamp,
                }
            )
        return dicts

    def __repr__(self) -> str:
        return f"<MarketCommoditiesDB(id={self.id}, station_id={self.station_id}, commodity_sym={self.commodity_sym})>"


class ShipsDB(BaseModel):
    __tablename__ = "ships"
    __table_args__ = {"schema": "core"}

    symbol: Mapped[str] = mapped_column(TEXT, primary_key=True)

    name: Mapped[Optional[str]] = mapped_column(TEXT)
    ship_id: Mapped[Optional[int]] = mapped_column(Integer)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    @staticmethod
    def to_dict_from_spansh(station_id: int, ship_id: int) -> dict[str, Any]:
        return {
            "station_id": station_id,
            "ship_id": ship_id,
        }

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
        TEXT, ForeignKey("core.ships.symbol"), nullable=False
    )  # Small lookup table; no index

    def __repr__(self) -> str:
        return f"<ShipyardShipsDB(id={self.id}, station_id={self.station_id}, ship_sym={self.ship_sym})>"


class ShipModulesDB(BaseModel):
    __tablename__ = "ship_modules"
    __table_args__ = {"schema": "core"}

    name: Mapped[str] = mapped_column(TEXT, primary_key=True)

    module_id: Mapped[Optional[int]] = mapped_column(Integer)
    symbol: Mapped[str] = mapped_column(TEXT)
    category: Mapped[Optional[str]] = mapped_column(TEXT)
    rating: Mapped[Optional[str]] = mapped_column(TEXT)
    ship: Mapped[Optional[str]] = mapped_column(TEXT)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    @staticmethod
    def to_dict_from_spansh(station_id: int, module_id: int) -> dict[str, Any]:
        return {
            "station_id": station_id,
            "module_id": module_id,
        }

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
        TEXT, ForeignKey("core.ship_modules.name"), nullable=False
    )  # Small lookup table; no index
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return f"<OutfittingShipModulesDB(id={self.id}, station_id={self.station_id}, module_name={self.module_name})>"


class ThargoidWarDB(BaseModelWithId):
    unique_columns = ("system_id",)
    __tablename__ = "thargoid_wars"
    __table_args__ = {"schema": "core"}

    system_id: Mapped[int] = mapped_column(Integer, ForeignKey("core.systems.id"), nullable=False, index=True)

    current_state: Mapped[str] = mapped_column(TEXT)
    days_remaining: Mapped[float] = mapped_column(Float)
    failure_state: Mapped[str] = mapped_column(TEXT)
    ports_remaining: Mapped[float] = mapped_column(Float)
    progress: Mapped[float] = mapped_column(Float)
    success_reached: Mapped[bool] = mapped_column(Boolean)
    success_state: Mapped[str] = mapped_column(TEXT)

    @staticmethod
    def to_dict_from_spansh(war: ThargoidWarSpansh) -> dict[str, Any]:
        # TODO: This isn't actually used oops
        return {
            "current_state": war.current_state,
            "days_remaining": war.days_remaining,
            "failure_state": war.failure_state,
            "ports_remaining": war.ports_remaining,
            "progress": war.progress,
            "success_reached": war.success_reached,
            "success_state": war.success_state,
        }

    def __repr__(self) -> str:
        return f"<ThargoidWarDB(id={self.id}, system_id={self.system_id}, current_state={self.current_state})>"


class FactionsDB(BaseModelWithId):
    unique_columns = ("name",)
    __tablename__ = "factions"
    __table_args__ = {"schema": "core"}

    name: Mapped[str] = mapped_column(TEXT, nullable=False, unique=True)

    allegiance: Mapped[Optional[str]] = mapped_column(TEXT)
    government: Mapped[Optional[str]] = mapped_column(TEXT)
    is_player: Mapped[Optional[bool]] = mapped_column(Boolean)

    faction_presences: Mapped[list["FactionPresencesDB"]] = relationship(back_populates="faction")

    @staticmethod
    def to_dict_from_spansh(spansh_faction: FactionSpansh | ControllingFactionSpansh) -> dict[str, Any]:
        return {
            "name": spansh_faction.name,
            "allegiance": spansh_faction.allegiance,
            "government": spansh_faction.government,
        }

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
    state: Mapped[Optional[str]] = mapped_column(TEXT)
    happiness: Mapped[Optional[str]] = mapped_column(TEXT)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    active_states: Mapped[Optional[list[str]]] = mapped_column(ARRAY(TEXT))

    pending_states: Mapped[Optional[list[str]]] = mapped_column(ARRAY(TEXT))
    recovering_states: Mapped[Optional[list[str]]] = mapped_column(ARRAY(TEXT))

    @staticmethod
    def to_dict_from_spansh(spansh_faction: FactionSpansh, system_id: int, faction_id: int) -> dict[str, Any]:
        return {
            "system_id": system_id,
            "faction_id": faction_id,
            "influence": spansh_faction.influence,
            "state": spansh_faction.state,
        }

    none_filter_bypass = ["happiness"]

    @staticmethod
    def to_dicts_from_eddn(
        eddn_model: journal_v1_0.Model, system_id: int, faction_name_to_id_mapping: dict[str, int]
    ) -> list[dict[str, Any]]:
        factions = eddn_model.message.Factions or []

        dicts: list[dict[str, Any]] = []
        for faction in factions:
            if faction.Name is None:
                logger.warning(f"Found a Faction without a Name! {pformat(faction)}")
                continue

            faction_id = faction_name_to_id_mapping.get(faction.Name)
            if faction_id is None:
                logger.warning(
                    "Found a Faction Name that wasn't in the provided id mapping: "
                    f"'{faction.Name}' - {pformat(faction_name_to_id_mapping)}"
                )
                continue
            d = {
                "system_id": system_id,
                "faction_id": faction_id,
                "influence": faction.Influence,
                "state": get_symbol_by_eddn_name(faction.FactionState) if faction.FactionState is not None else None,
                "happiness": get_symbol_by_eddn_name(faction.Happiness) if faction.Happiness is not None else None,
                "updated_at": eddn_model.message.timestamp,
                "active_states": [get_symbol_by_eddn_name(state.State) for state in faction.ActiveStates or []],
                "pending_states": [get_symbol_by_eddn_name(state.State) for state in faction.PendingStates or []],
                "recovering_states": [get_symbol_by_eddn_name(state.State) for state in faction.RecoveringStates or []],
            }

            d_filtered = {k: v for k, v in d.items() if v is not None or k in FactionPresencesDB.none_filter_bypass}
            dicts.append(d_filtered)

        return dicts

    def __repr__(self) -> str:
        return f"<FactionPresencesDB(id={self.id}, system_id={self.system_id}, faction_id={self.faction_id})>"


class SystemsDB(BaseModelWithId):
    unique_columns = ("name",)
    __tablename__ = "systems"
    __table_args__ = {"schema": "core"}

    name: Mapped[str] = mapped_column(TEXT, nullable=False, unique=True)

    id64: Mapped[Optional[int]] = mapped_column(BigInteger)
    id_spansh: Mapped[Optional[int]] = mapped_column(BigInteger)
    id_edsm: Mapped[Optional[int]] = mapped_column(BigInteger)

    x: Mapped[float] = mapped_column(Float)
    y: Mapped[float] = mapped_column(Float)
    z: Mapped[float] = mapped_column(Float)
    coords: Mapped[WKBElement] = mapped_column(Geometry(geometry_type="POINTZ", srid=0))

    date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    allegiance: Mapped[Optional[str]] = mapped_column(TEXT)
    population: Mapped[Optional[int]] = mapped_column(BigInteger)
    primary_economy: Mapped[Optional[str]] = mapped_column(TEXT)
    secondary_economy: Mapped[Optional[str]] = mapped_column(TEXT)
    security: Mapped[Optional[str]] = mapped_column(TEXT)
    government: Mapped[Optional[str]] = mapped_column(TEXT)
    body_count: Mapped[Optional[int]] = mapped_column(Integer)
    controlling_power: Mapped[Optional[str]] = mapped_column(TEXT)
    power_conflict_progress: Mapped[Optional[list[dict[str, float]]]] = mapped_column(JSONB)
    power_state: Mapped[Optional[str]] = mapped_column(TEXT)
    power_state_control_progress: Mapped[Optional[float]] = mapped_column(Float)
    power_state_reinforcement: Mapped[Optional[float]] = mapped_column(Float)
    power_state_undermining: Mapped[Optional[float]] = mapped_column(Float)
    powers: Mapped[Optional[list[str]]] = mapped_column(ARRAY(TEXT))
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

    @staticmethod
    def coords_spansh_to_wkbelement(coords: CoordinatesSpansh) -> WKBElement:
        return from_shape(Point(coords.x, coords.y, coords.z), srid=0)

    @staticmethod
    def power_conflict_progress_to_dict_from_spansh(participant: PowerConflictProgressSpansh) -> dict[str, str | float]:
        return {
            "power": participant.power,
            "progress": participant.progress,
        }

    @staticmethod
    def to_dict_from_spansh(spansh_system: SystemSpansh, controlling_faction_id: int | None) -> dict[str, Any]:
        return {
            "allegiance": spansh_system.allegiance,
            "controlling_faction_id": controlling_faction_id,
            "x": spansh_system.coords.x,
            "y": spansh_system.coords.y,
            "z": spansh_system.coords.z,
            "coords": SystemsDB.coords_spansh_to_wkbelement(spansh_system.coords),
            "date": spansh_system.date,
            "government": spansh_system.government,
            "id64": spansh_system.id64,
            "name": spansh_system.name,
            "population": spansh_system.population,
            "primary_economy": spansh_system.primary_economy,
            "secondary_economy": spansh_system.secondary_economy,
            "security": spansh_system.security,
            "body_count": spansh_system.body_count,
            "controlling_power": spansh_system.controlling_power,
            "power_conflict_progress": [
                SystemsDB.power_conflict_progress_to_dict_from_spansh(participant)
                for participant in spansh_system.power_conflict_progress or []
            ],
            "power_state": spansh_system.power_state,
            "power_state_control_progress": spansh_system.power_state_control_progress,
            "power_state_reinforcement": spansh_system.power_state_reinforcement,
            "power_state_undermining": spansh_system.power_state_undermining,
            "powers": spansh_system.powers,
            # "thargoid_war": (
            #   spansh_system.thargoid_war.to_sqlalchemy_dict()
            #   if spansh_system.thargoid_war is not None else None
            # ),
            "controlling_power_updated_at": getattr(spansh_system.timestamps, "controlling_power", None),
            "power_state_updated_at": getattr(spansh_system.timestamps, "power_state", None),
            "powers_updated_at": getattr(spansh_system.timestamps, "powers", None),
        }

    @staticmethod
    def starpos_to_wkbelement(coords: tuple[float, float, float]) -> WKBElement:
        return from_shape(Point(coords[0], coords[1], coords[2]), srid=0)

    @staticmethod
    def to_dict_from_eddn(eddn_model: journal_v1_0.Model, controlling_faction_id: int | None) -> dict[str, Any]:
        """
        StarSystem='Catun',
        StarPos=[-4.71875, 25.625, -105.0625],
        SystemAddress=2621817489755,
        Body='Catun',
        BodyID=0,
        BodyType='Star',
        Conflicts=[{
            'Faction1': {'Name': 'Catun PLC', 'Stake': 'Moon Survey', 'WonDays': 0},
            'Faction2': {'Name': 'Catun Resistance', 'Stake': 'Schunmann Cultivation Holdings', 'WonDays': 0},
            'Status': 'pending',
            'WarType': 'civilwar'
        }],
        SystemFaction={'FactionState': 'Expansion', 'Name': 'Caballeros de Sion'},
        """
        msg = eddn_model.message
        government = getattr(msg, "SystemGovernment", None)
        primary_economy = getattr(msg, "SystemEconomy", None)
        secondary_economy = getattr(msg, "SystemSecondEconomy", None)
        security = getattr(msg, "SystemSecurity", None)

        starpos = tuple(msg.StarPos)
        if len(starpos) != 3:
            logger.warning(f"Got a malformed StarPos value! '{msg.StarPos}' - '{pformat(msg)}'")
            raise ValueError(f"Malformed StarPos! '{msg.StarPos}'")

        d = {
            "allegiance": getattr(msg, "SystemAllegiance", None),
            "controlling_faction_id": controlling_faction_id,
            "x": starpos[0],
            "y": starpos[1],
            "z": starpos[2],
            "coords": SystemsDB.starpos_to_wkbelement(starpos),
            "date": msg.timestamp,
            "government": get_symbol_by_eddn_name(cast(str, government)) if government is not None else None,
            # "id64": msg.SystemAddress, # Never update id64?
            "name": msg.StarSystem,
            "population": getattr(msg, "Population", None),
            "primary_economy": (
                get_symbol_by_eddn_name(cast(str, primary_economy)) if primary_economy is not None else None
            ),
            "secondary_economy": (
                get_symbol_by_eddn_name(cast(str, secondary_economy)) if secondary_economy is not None else None
            ),
            "security": get_symbol_by_eddn_name(cast(str, security)) if security is not None else None,
            "controlling_power": getattr(msg, "ControllingPower", None),
            # "power_conflict_progress": [
            #     SystemsDB.power_conflict_progress_to_dict_from_spansh(participant)
            #     for participant in getattr(msg, "power_conflict_progress or []
            # ],
            "power_state": getattr(msg, "PowerplayState", None),
            "power_state_control_progress": getattr(msg, "PowerplayStateControlProgress", None),
            "power_state_reinforcement": getattr(msg, "PowerplayStateReinforcement", None),
            "power_state_undermining": getattr(msg, "PowerplayStateUndermining", None),
            "powers": getattr(msg, "Powers", None),
            # "thargoid_war": (
            #   spansh_system.thargoid_war.to_sqlalchemy_dict()
            #   if spansh_system.thargoid_war is not None else None
            # ),
            "controlling_power_updated_at": msg.timestamp,
            "power_state_updated_at": msg.timestamp,
            "powers_updated_at": msg.timestamp,
        }

        return {k: v for k, v in d.items() if v is not None}

    def __repr__(self) -> str:
        return f"<SystemsDB(id={self.id}, name={self.name!r})>"
