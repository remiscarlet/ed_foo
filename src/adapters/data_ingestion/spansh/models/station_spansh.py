from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from dataclasses_json import DataClassJsonMixin, config, dataclass_json


@dataclass(kw_only=True)
class CommodityPriceSpansh(DataClassJsonMixin):
    buyPrice: int
    demand: int
    sellPrice: int
    supply: int
    updateTime: Optional[datetime] = None


@dataclass_json
@dataclass
class CommoditySpansh(CommodityPriceSpansh):
    category: str  # src.core.models.commodity.CommodityCategory
    commodityId: int
    name: str
    symbol: str


@dataclass_json
@dataclass
class MarketSpansh(DataClassJsonMixin):
    commodities: Optional[List[CommoditySpansh]] = None
    prohibitedCommodities: Optional[List[str]] = None
    updateTime: Optional[datetime] = None


@dataclass_json
@dataclass
class ShipModuleSpansh(DataClassJsonMixin):
    category: str
    cls: int = field(metadata=config(field_name="class"))
    moduleId: int
    name: str
    rating: str
    symbol: str

    ship: Optional[str] = None


@dataclass_json
@dataclass
class OutfittingSpansh(DataClassJsonMixin):
    modules: List[ShipModuleSpansh]
    updateTime: datetime


@dataclass_json
@dataclass
class ShipSpansh(DataClassJsonMixin):
    name: str
    shipId: int
    symbol: str


@dataclass_json
@dataclass
class ShipyardSpansh(DataClassJsonMixin):
    ships: List[ShipSpansh]
    updateTime: datetime


@dataclass_json
@dataclass
class StationSpansh(DataClassJsonMixin):
    id: int
    name: str
    updateTime: datetime

    allegiance: Optional[str] = None
    controllingFaction: Optional[str] = None
    controllingFactionState: Optional[str] = None
    distanceToArrival: Optional[float] = None
    economies: Optional[Dict[str, float]] = None
    government: Optional[str] = None
    landingPads: Optional[Dict[str, int]] = None
    market: Optional[MarketSpansh] = None
    outfitting: Optional[OutfittingSpansh] = None
    primaryEconomy: Optional[str] = None
    services: Optional[List[str]] = None
    shipyard: Optional[ShipyardSpansh] = None
    type: Optional[str] = None

    carrierName: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
