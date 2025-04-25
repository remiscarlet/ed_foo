from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from dataclasses_json import DataClassJsonMixin, config, dataclass_json
from src.types.commodities import CommodityCategory


@dataclass(kw_only=True)
class CommodityPriceDTO(DataClassJsonMixin):
    buyPrice: int
    demand: int
    sellPrice: int
    supply: int
    updateTime: Optional[datetime] = None


@dataclass_json
@dataclass
class CommodityDTO(CommodityPriceDTO):
    category: CommodityCategory
    commodityId: int
    name: str
    symbol: str


@dataclass_json
@dataclass
class MarketDTO(DataClassJsonMixin):
    commodities: Optional[List[CommodityDTO]] = None
    prohibitedCommodities: Optional[List[str]] = None
    updateTime: Optional[datetime] = None


@dataclass_json
@dataclass
class ShipModuleDTO(DataClassJsonMixin):
    category: str
    cls: int = field(metadata=config(field_name="class"))
    moduleId: int
    name: str
    rating: str
    symbol: str

    ship: Optional[str] = None


@dataclass_json
@dataclass
class OutfittingDTO(DataClassJsonMixin):
    modules: List[ShipModuleDTO]
    updateTime: datetime


@dataclass_json
@dataclass
class ShipDTO(DataClassJsonMixin):
    name: str
    shipId: int
    symbol: str


@dataclass_json
@dataclass
class ShipyardDTO(DataClassJsonMixin):
    ships: List[ShipDTO]
    updateTime: datetime


@dataclass_json
@dataclass
class StationDTO(DataClassJsonMixin):
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
    market: Optional[MarketDTO] = None
    outfitting: Optional[OutfittingDTO] = None
    primaryEconomy: Optional[str] = None
    services: Optional[List[str]] = None
    shipyard: Optional[ShipyardDTO] = None
    type: Optional[str] = None

    carrierName: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
