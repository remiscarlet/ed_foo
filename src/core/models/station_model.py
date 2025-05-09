from datetime import datetime

from pydantic import BaseModel


class CommodityPrice(BaseModel):
    buy_price: int
    demand: int
    sell_price: int
    supply: int
    updated_at: datetime | None = None


class Commodity(CommodityPrice):
    category: str  # src.core.models.commodity.CommodityCategory
    commodity_sym: str
    name: str
    symbol: str


class Market(BaseModel):
    commodities: list[Commodity] | None = None
    prohibited_commodities: list[str] | None = None
    updated_at: datetime | None = None


class ShipModule(BaseModel):
    category: str
    cls: int
    module_id: int
    name: str
    rating: str
    symbol: str

    ship: str | None = None


class Outfitting(BaseModel):
    modules: list[ShipModule]
    updated_at: datetime | None = None


class Ship(BaseModel):
    name: str
    ship_id: int
    symbol: str


class Shipyard(BaseModel):
    ships: list[Ship]
    updated_at: datetime | None = None


class Station(BaseModel):
    name: str

    id64: int | None = None
    id_spansh: int | None = None
    id_edsm: int | None = None
    updated_at: datetime | None = None

    allegiance: str | None = None
    controlling_faction: str | None = None
    controlling_faction_state: str | None = None
    distance_to_arrival: float | None = None
    economies: dict[str, float] | None = None
    government: str | None = None
    landing_pads: dict[str, int] | None = None
    market: Market | None = None
    outfitting: Outfitting | None = None
    primary_economy: str | None = None
    services: list[str] | None = None
    shipyard: Shipyard | None = None
    type: str | None = None

    carrier_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    spansh_updated_at: datetime | None = None
    edsm_updated_at: datetime | None = None
    eddn_updated_at: datetime | None = None
