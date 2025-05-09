from datetime import datetime
from typing import Any, Tuple

from pydantic import Field

from src.common.logging import get_logger
from src.ingestion.spansh.models import BaseSpanshModel

logger = get_logger(__name__)


class CommodityPriceSpansh(BaseSpanshModel):
    buy_price: int
    demand: int
    sell_price: int
    supply: int
    updated_at: datetime | None = None
    _validate_updated_at = BaseSpanshModel.flexible_datetime_validator("updated_at")


class CommoditySpansh(CommodityPriceSpansh):
    category: str  # src.core.models.commodity.CommodityCategory
    commodity_id: int
    name: str
    symbol: str

    def to_cache_key_tuple(self, station_id: int, commodity_symbol: str) -> Tuple[Any, ...]:
        return (self.__class__, station_id, commodity_symbol)

    def to_sqlalchemy_dict(self, station_id: int, commodity_sym: str) -> dict[str, Any]:
        return {
            "station_id": station_id,
            "commodity_sym": commodity_sym,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
            "supply": self.supply,
            "demand": self.demand,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def to_blacklisted_sqlalchemy_dict(station_id: int, commodity_sym: str) -> dict[str, Any]:
        return {
            "station_id": station_id,
            "commodity_sym": commodity_sym,
            "is_blacklisted": True,
            "buy_price": None,
            "sell_price": None,
            "supply": None,
            "demand": None,
            "updated_at": None,
        }


class MarketSpansh(BaseSpanshModel):
    commodities: list[CommoditySpansh] | None = None
    prohibited_commodities: list[str] | None = None
    update_time: datetime | None = None
    _validate_update_time = BaseSpanshModel.flexible_datetime_validator("update_time")


class ShipModuleSpansh(BaseSpanshModel):
    category: str
    cls: int = Field(alias="class")
    module_id: int
    name: str
    rating: str
    symbol: str

    ship: str | None = None

    def to_sqlalchemy_dict(self, station_id: int, module_id: int) -> dict[str, Any]:
        return {
            "station_id": station_id,
            "module_id": module_id,
        }


class OutfittingSpansh(BaseSpanshModel):
    modules: list[ShipModuleSpansh]
    updated_at: datetime | None = None
    _validate_updated_at = BaseSpanshModel.flexible_datetime_validator("updated_at")


class ShipSpansh(BaseSpanshModel):
    name: str
    ship_id: int
    symbol: str

    def to_sqlalchemy_dict(self, station_id: int, ship_id: int) -> dict[str, Any]:
        return {
            "station_id": station_id,
            "ship_id": ship_id,
        }


class ShipyardSpansh(BaseSpanshModel):
    ships: list[ShipSpansh]
    updated_at: datetime | None = None
    _validate_updated_at = BaseSpanshModel.flexible_datetime_validator("updated_at")


class StationSpansh(BaseSpanshModel):
    def __repr__(self) -> str:
        return f"StationsSpansh(id: {self.id}, name: {self.name})"

    def to_cache_key_tuple(self, owner_id: int) -> Tuple[Any, ...]:
        # return ("StationsDB", owner_id, self.name)
        tup = ("StationsDB", owner_id, self.name)
        logger.trace(f"STATIONS SPANSH TO CACHE KEY TUPLE: {tup}")
        return tup

    id: int
    name: str
    updated_at: datetime | None = None
    _validate_updated_at = BaseSpanshModel.flexible_datetime_validator("updated_at")

    allegiance: str | None = None
    controlling_faction: str | None = None
    controlling_faction_state: str | None = None
    distance_to_arrival: float | None = None
    economies: dict[str, float] | None = None
    government: str | None = None
    landing_pads: dict[str, int] | None = None
    market: MarketSpansh | None = None
    outfitting: OutfittingSpansh | None = None
    primary_economy: str | None = None
    services: list[str] | None = None
    shipyard: ShipyardSpansh | None = None
    type: str | None = None

    carrier_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    def to_sqlalchemy_dict(self, owner_id: int, owner_type: str) -> dict[str, Any]:
        if self.landing_pads is not None:
            large_pads = self.landing_pads.get("large", 0)
            medium_pads = self.landing_pads.get("medium", 0)
            small_pads = self.landing_pads.get("small", 0)
        else:
            large_pads = 0
            medium_pads = 0
            small_pads = 0
        return {
            "id_spansh": self.id,
            "owner_id": owner_id,
            "owner_type": owner_type,
            "name": self.name,
            "allegiance": self.allegiance,
            "controlling_faction": self.controlling_faction,
            "controlling_faction_state": self.controlling_faction_state,
            "distance_to_arrival": self.distance_to_arrival,
            "economies": self.economies,
            "government": self.government,
            "large_landing_pads": large_pads,
            "medium_landing_pads": medium_pads,
            "small_landing_pads": small_pads,
            "primary_economy": self.primary_economy,
            "prohibited_commodities": self.market.prohibited_commodities if self.market is not None else None,
            "services": self.services,
            "type": self.type,
            "carrier_name": self.carrier_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "spansh_updated_at": self.updated_at,
        }
