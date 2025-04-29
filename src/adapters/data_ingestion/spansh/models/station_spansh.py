from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from dataclasses_json import DataClassJsonMixin, config, dataclass_json


@dataclass(kw_only=True)
class CommodityPriceSpansh(DataClassJsonMixin):
    buy_price: int
    demand: int
    sell_price: int
    supply: int
    updated_at: Optional[datetime] = None


@dataclass_json
@dataclass
class CommoditySpansh(CommodityPriceSpansh):
    category: str  # src.core.models.commodity.CommodityCategory
    commodity_id: int
    name: str
    symbol: str


@dataclass_json
@dataclass
class MarketSpansh(DataClassJsonMixin):
    commodities: Optional[List[CommoditySpansh]] = None
    prohibited_commodities: Optional[List[str]] = None
    updated_at: Optional[datetime] = None


@dataclass_json
@dataclass
class ShipModuleSpansh(DataClassJsonMixin):
    category: str
    cls: int = field(metadata=config(field_name="class"))
    module_id: int
    name: str
    rating: str
    symbol: str

    ship: Optional[str] = None


@dataclass_json
@dataclass
class OutfittingSpansh(DataClassJsonMixin):
    modules: List[ShipModuleSpansh]
    updated_at: datetime


@dataclass_json
@dataclass
class ShipSpansh(DataClassJsonMixin):
    name: str
    ship_id: int
    symbol: str


@dataclass_json
@dataclass
class ShipyardSpansh(DataClassJsonMixin):
    ships: List[ShipSpansh]
    updated_at: datetime


@dataclass_json
@dataclass
class StationSpansh(DataClassJsonMixin):
    id: int
    name: str
    updated_at: datetime

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
