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


class OutfittingSpansh(BaseSpanshModel):
    modules: list[ShipModuleSpansh]
    updated_at: datetime | None = None
    _validate_updated_at = BaseSpanshModel.flexible_datetime_validator("updated_at")


class ShipSpansh(BaseSpanshModel):
    name: str
    ship_id: int
    symbol: str


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
    update_time: datetime | None = None
    _validate_update_time = BaseSpanshModel.flexible_datetime_validator("update_time")

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
