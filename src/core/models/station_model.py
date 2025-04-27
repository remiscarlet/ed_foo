from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CommodityPrice(BaseModel):
    buyPrice: int
    demand: int
    sellPrice: int
    supply: int
    updateTime: Optional[datetime] = None


class Commodity(BaseModel):
    category: str  # src.core.models.commodity.CommodityCategory
    commodityId: int
    name: str
    symbol: str


class Market(BaseModel):
    commodities: Optional[List[Commodity]] = None
    prohibitedCommodities: Optional[List[str]] = None
    updateTime: Optional[datetime] = None


class ShipModule(BaseModel):
    category: str
    cls: int = Field(alias="class")
    moduleId: int
    name: str
    rating: str
    symbol: str

    ship: Optional[str] = None


class Outfitting(BaseModel):
    modules: List[ShipModule]
    updateTime: datetime


class Ship(BaseModel):
    name: str
    shipId: int
    symbol: str


class Shipyard(BaseModel):
    ships: List[Ship]
    updateTime: datetime


class Station(BaseModel):
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
    market: Optional[Market] = None
    outfitting: Optional[Outfitting] = None
    primaryEconomy: Optional[str] = None
    services: Optional[List[str]] = None
    shipyard: Optional[Shipyard] = None
    type: Optional[str] = None

    carrierName: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
