from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CommodityPrice(BaseModel):
    buy_price: int
    demand: int
    sell_price: int
    supply: int
    update_time: Optional[datetime] = None


class Commodity(BaseModel):
    category: str  # src.core.models.commodity.CommodityCategory
    commodity_id: int
    name: str
    symbol: str


class Market(BaseModel):
    commodities: Optional[List[Commodity]] = None
    prohibited_commodities: Optional[List[str]] = None
    update_time: Optional[datetime] = None


class ShipModule(BaseModel):
    category: str
    cls: int = Field(alias="class")
    module_id: int
    name: str
    rating: str
    symbol: str

    ship: Optional[str] = None


class Outfitting(BaseModel):
    modules: List[ShipModule]
    update_time: datetime


class Ship(BaseModel):
    name: str
    ship_id: int
    symbol: str


class Shipyard(BaseModel):
    ships: List[Ship]
    update_time: datetime


class Station(BaseModel):
    id: int
    name: str
    updateTime: datetime

    allegiance: Optional[str] = None
    controlling_faction: Optional[str] = None
    controlling_faction_state: Optional[str] = None
    distance_to_Arrival: Optional[float] = None
    economies: Optional[Dict[str, float]] = None
    government: Optional[str] = None
    landing_pads: Optional[Dict[str, int]] = None
    market: Optional[Market] = None
    outfitting: Optional[Outfitting] = None
    primary_economy: Optional[str] = None
    services: Optional[List[str]] = None
    shipyard: Optional[Shipyard] = None
    type: Optional[str] = None

    carrier_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
