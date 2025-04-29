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
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.adapters.persistence.postgresql import BaseModel
from src.adapters.persistence.postgresql.body_db import BodiesDB
from src.adapters.persistence.postgresql.system_db import SystemsDB


class StationsDB(BaseModel):
    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(primary_key=True)
    id64: Mapped[Optional[int]] = mapped_column(BigInteger)
    spansh_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    edsm_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

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
    def parent(self) -> Union[SystemsDB, BodiesDB]:
        session = Session.object_session(self)
        if session is None:
            raise Exception("Could not find a valid Session attached to StationsDB object!")

        parent: Optional[Union[SystemsDB, BodiesDB]] = None
        if self.owner_type == "system":
            parent = session.query(SystemsDB).filter_by(id=self.owner_id).first()
        elif self.owner_type == "body":
            parent = session.query(BodiesDB).filter_by(id=self.owner_id).first()
        else:
            raise ValueError(f"Unknown owner_type: {self.owner_type}")

        if parent is None:
            raise Exception("Could not find a valid parent object!")

        return parent


class CommoditiesDB(BaseModel):
    __tablename__ = "commodities"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(Text)
    is_mineable: Mapped[Optional[bool]] = mapped_column(Boolean)
    ring_types: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))
    mining_method: Mapped[Optional[str]] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<CommoditiesDB(id={self.id}, name={self.name!r})>"


class MarketCommoditiesDB(BaseModel):
    __tablename__ = "market_commodities"

    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("stations.id"), nullable=False)
    commodity_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("commodities.id"), nullable=False)

    buy_price: Mapped[Optional[int]] = mapped_column(Integer)
    sell_price: Mapped[Optional[int]] = mapped_column(Integer)
    stock: Mapped[Optional[int]] = mapped_column(BigInteger)
    demand: Mapped[Optional[int]] = mapped_column(BigInteger)
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    is_blacklisted: Mapped[Optional[bool]] = mapped_column(Boolean)

    def __repr__(self) -> str:
        return f"<MarketCommoditiesDB(id={self.id}, station_id={self.station_id}, commodity_id={self.commodity_id})>"


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
