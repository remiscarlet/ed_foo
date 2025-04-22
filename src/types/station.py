from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from dataclasses_json import DataClassJsonMixin, config, dataclass_json


@dataclass(kw_only=True)
class CommodityPrice(DataClassJsonMixin):
    buyPrice: int
    demand: int
    sellPrice: int
    supply: int
    updateTime: Optional[datetime] = None

    def __repr__(self) -> str:
        return (
            f"CommodityPrice(buyPrice={self.buyPrice}, demand={self.demand}, "
            f"sellPrice={self.sellPrice}, supply={self.supply}, updateTime={self.updateTime})"
        )


@dataclass_json
@dataclass
class Commodity(CommodityPrice):
    category: str
    commodityId: int
    name: str
    symbol: str


@dataclass_json
@dataclass
class Market(DataClassJsonMixin):
    commodities: Optional[List[Commodity]] = None
    prohibitedCommodities: Optional[List[str]] = None
    updateTime: Optional[datetime] = None


@dataclass_json
@dataclass
class ShipModule(DataClassJsonMixin):
    category: str
    cls: int = field(metadata=config(field_name="class"))
    moduleId: int
    name: str
    rating: str
    symbol: str

    ship: Optional[str] = None


@dataclass_json
@dataclass
class Outfitting(DataClassJsonMixin):
    modules: List[ShipModule]
    updateTime: datetime


@dataclass_json
@dataclass
class Ship(DataClassJsonMixin):
    name: str
    shipId: int
    symbol: str


@dataclass_json
@dataclass
class Shipyard(DataClassJsonMixin):
    ships: List[Ship]
    updateTime: datetime


@dataclass_json
@dataclass
class Station(DataClassJsonMixin):
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

    def has_commodities(self, target_commodity_names: List[str], require_all: bool = True) -> bool:
        if self.market is None:
            return False
        if not self.market.commodities:
            return False

        expected_commodities = set(target_commodity_names)
        market_commodities = set(map(lambda commodity: commodity.name, self.market.commodities))

        found_commodities = expected_commodities.intersection(market_commodities)

        if require_all:
            return found_commodities == expected_commodities
        else:
            return len(found_commodities) > 0

    def get_commodity_price(self, target_commodity_name: str) -> Optional[CommodityPrice]:
        if self.market is None:
            return None
        if not self.market.commodities:
            return None

        for commodity in self.market.commodities:
            if commodity.name == target_commodity_name:
                return CommodityPrice(
                    buyPrice=commodity.buyPrice,
                    demand=commodity.demand,
                    sellPrice=commodity.sellPrice,
                    supply=commodity.supply,
                )

        return None

    def has_minimum_landing_pad(self, min_landing_pad_size: str) -> bool:
        return (
            self.landingPads is not None
            and min_landing_pad_size in self.landingPads
            and self.landingPads[min_landing_pad_size] > 0
        )

    def has_min_data_age_days(self, min_age_days: int) -> bool:
        return (datetime.now(timezone.utc) - self.updateTime) > timedelta(days=min_age_days)
