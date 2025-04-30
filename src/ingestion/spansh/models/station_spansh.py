from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field

from src.core.models.station_model import (
    Commodity,
    Market,
    Outfitting,
    Ship,
    ShipModule,
    Shipyard,
    Station,
)
from src.core.ports.converter_port import ToCoreModel
from src.ingestion.spansh.models import BaseSpanshModel


class CommodityPriceSpansh(BaseSpanshModel):
    buy_price: int
    demand: int
    sell_price: int
    supply: int
    updated_at: Optional[datetime] = None
    _validate_updated_at = BaseSpanshModel.flexible_datetime_validator("updated_at")


class CommoditySpansh(CommodityPriceSpansh):
    category: str  # src.core.models.commodity.CommodityCategory
    commodity_id: int
    name: str
    symbol: str


class MarketSpansh(BaseSpanshModel):
    commodities: Optional[List[CommoditySpansh]] = None
    prohibited_commodities: Optional[List[str]] = None
    updated_at: Optional[datetime] = None
    _validate_updated_at = BaseSpanshModel.flexible_datetime_validator("updated_at")


class ShipModuleSpansh(BaseSpanshModel):
    category: str
    cls: int = Field(alias="class")
    module_id: int
    name: str
    rating: str
    symbol: str

    ship: Optional[str] = None

    def to_core_model(self) -> ShipModule:
        return ShipModule(
            category=self.category,
            cls=self.cls,
            module_id=self.module_id,
            name=self.name,
            rating=self.rating,
            symbol=self.symbol,
            ship=self.ship,
        )


class OutfittingSpansh(BaseSpanshModel, ToCoreModel[Outfitting]):
    modules: List[ShipModuleSpansh]
    updated_at: Optional[datetime] = None
    _validate_updated_at = BaseSpanshModel.flexible_datetime_validator("updated_at")

    def to_core_model(self) -> Outfitting:
        return Outfitting(
            modules=[module.to_core_model() for module in self.modules or []],
            updated_at=self.updated_at,
        )


class ShipSpansh(BaseSpanshModel, ToCoreModel[Ship]):
    name: str
    ship_id: int
    symbol: str

    def to_core_model(self) -> Ship:
        return Ship(
            name=self.name,
            ship_id=self.ship_id,
            symbol=self.symbol,
        )


class ShipyardSpansh(BaseSpanshModel, ToCoreModel[Shipyard]):
    ships: List[ShipSpansh]
    updated_at: Optional[datetime] = None
    _validate_updated_at = BaseSpanshModel.flexible_datetime_validator("updated_at")

    def to_core_model(self) -> Shipyard:
        return Shipyard(
            ships=[ship.to_core_model() for ship in self.ships or []],
            updated_at=self.updated_at,
        )


class StationSpansh(BaseSpanshModel, ToCoreModel[Station]):
    def __hash__(self) -> str:
        return hash((type(self),), (self.id, self.name))

    id: int
    name: str
    updated_at: Optional[datetime] = None
    _validate_updated_at = BaseSpanshModel.flexible_datetime_validator("updated_at")

    allegiance: Optional[str] = None
    controlling_faction: Optional[str] = None
    controlling_faction_state: Optional[str] = None
    distance_to_arrival: Optional[float] = None
    economies: Optional[Dict[str, float]] = None
    government: Optional[str] = None
    landing_pads: Optional[Dict[str, int]] = None
    market: Optional[MarketSpansh] = None
    outfitting: Optional[OutfittingSpansh] = None
    primary_economy: Optional[str] = None
    services: Optional[List[str]] = None
    shipyard: Optional[ShipyardSpansh] = None
    type: Optional[str] = None

    carrier_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def to_core_model(self) -> Station:
        return Station(
            id=self.id,
            name=self.name,
            updated_at=self.updated_at,
            allegiance=self.allegiance,
            controlling_faction=self.controlling_faction,
            controlling_faction_state=self.controlling_faction_state,
            distance_to_arrival=self.distance_to_arrival,
            economies=self.economies,
            government=self.government,
            landing_pads=self.landing_pads,
            market=self.market.to_core_model() if self.market is not None else None,
            outfitting=self.outfitting.to_core_model() if self.outfitting is not None else None,
            primary_economy=self.primary_economy,
            services=self.services,
            shipyard=self.shipyard.to_core_model() if self.shipyard is not None else None,
            type=self.type,
            carrier_name=self.carrier_name,
            latitude=self.latitude,
            longitude=self.longitude,
        )
