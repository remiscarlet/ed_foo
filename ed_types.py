import dataclasses
import json
import pprint
from dataclasses_json import config, dataclass_json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass_json
@dataclass
class ControllingFaction:
    allegiance: Optional[str] = None
    government: Optional[str] = None
    name: Optional[str] = None


@dataclass_json
@dataclass
class Coordinates:
    x: float
    y: float
    z: float

    def distance_to(self, other: "Coordinates") -> float:
        dx = (self.x - other.x) ** 2
        dy = (self.y - other.y) ** 2
        dz = (self.z - other.z) ** 2
        return (dx + dy + dz) ** (0.5)


@dataclass_json
@dataclass
class Timestamps:
    controllingPower: Optional[str] = None
    powerState: Optional[str] = None
    powers: Optional[str] = None


@dataclass
class CommodityPrice:
    buyPrice: int
    demand: int
    sellPrice: int
    supply: int


@dataclass_json
@dataclass
class Commodity(CommodityPrice):
    category: str
    commodityId: int
    name: str
    symbol: str


@dataclass_json
@dataclass
class Market:
    commodities: Optional[List[Commodity]] = None
    prohibitedCommodities: Optional[List[str]] = None
    updateTime: Optional[str] = None


@dataclass_json
@dataclass
class ShipModule:
    category: str
    cls: int = field(metadata=config(field_name="class"))
    moduleId: int
    name: str
    rating: str
    symbol: str

    ship: Optional[str] = None


@dataclass_json
@dataclass
class Outfitting:
    modules: List[ShipModule]
    updateTime: str


@dataclass_json
@dataclass
class Ship:
    name: str
    shipId: int
    symbol: str


@dataclass_json
@dataclass
class Shipyard:
    ships: List[Ship]
    updateTime: str


@dataclass_json
@dataclass
class Station:
    id: int
    name: str
    updateTime: str

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

    def has_commodities(self, target_commodity_names: List[str], require_all=True):
        if self.market is None:
            return False
        if not self.market.commodities:
            return False

        expected_commodities = set(target_commodity_names)
        market_commodities = set(
            map(lambda commodity: commodity.name, self.market.commodities)
        )

        found_commodities = expected_commodities.intersection(market_commodities)

        if require_all:
            return found_commodities == expected_commodities
        else:
            return len(found_commodities) > 0

    def get_commodity_price(
        self, target_commodity_name: str
    ) -> Optional[CommodityPrice]:
        if self.market is None:
            return False
        if not self.market.commodities:
            return False

        for commodity in self.market.commodities:
            if commodity.name == target_commodity_name:
                return CommodityPrice(
                    commodity.buyPrice,
                    commodity.demand,
                    commodity.sellPrice,
                    commodity.supply,
                )

        return None

    def has_minimum_landing_pad(self, min_landing_pad_size: str) -> bool:
        return (
            self.landingPads is not None
            and min_landing_pad_size in self.landingPads
            and self.landingPads[min_landing_pad_size] > 0
        )


def _default_serialize(o):
    if hasattr(o, "to_dict"):
        return o.to_dict()
    raise TypeError(f"Type {o!r} not serializable")

@dataclass_json
@dataclass
class System:
    allegiance: str
    bodies: List[Any]
    controllingFaction: ControllingFaction
    coords: Coordinates
    date: str
    factions: List[Any]
    government: str
    id64: int
    name: str
    population: int
    primaryEconomy: str
    secondaryEconomy: str
    security: str
    stations: List[Station]

    bodyCount: Optional[int] = None

    controllingPower: Optional[str] = None
    powerConflictProgress: Optional[List[Any]] = None
    powerState: Optional[str] = None
    powerStateControlProgress: Optional[float] = None
    powerStateReinforcement: Optional[float] = None
    powerStateUndermining: Optional[float] = None
    powers: Optional[List[str]] = None

    thargoidWar: Optional[int] = None
    timestamps: Optional[Timestamps] = None

    def __post_init__(self):
        self.column_names = [field.name for field in dataclasses.fields(self)]

    def distance_to(self, target_system: "System"):
        return self.coords.distance_to(target_system.coords)

    def is_in_powerplay(self):
        return self.powers is not None and len(self.powers) > 0

    def get_stations_with_services(self, services: List[str]) -> List[Station]:
        expected_services = set(services)

        stations = []
        for station in self.stations:
            if isinstance(station, dict):
                pprint.pprint(station, depth=2)
            available_services = (
                set() if station.services is None else set(station.services)
            )
            if expected_services.intersection(available_services):
                stations.append(station)

        return stations

    def db_table_name(self):
        return "system"

    def db_column_list(self):
        return ", ".join(self.column_names)


    def db_values_list(self):
        rtn = ""
        for column_name in self.column_names:
            col_val = getattr(self, column_name)
            if col_val is None:
                rtn += f"    null,\n"
            elif isinstance(col_val, int) or isinstance(col_val, float):
                rtn += f"    {col_val},\n"
            else:
                try:
                    s = col_val.to_json()
                except (AttributeError, TypeError):
                    s = json.dumps(col_val, default=_default_serialize)
                s = s.replace("'", "''")
                rtn += f"    '{s}',\n"
        rtn = rtn[:-2]  # Strip last newline + comma
        return rtn


@dataclass_json
@dataclass
class PowerplaySystem:
    power: str
    powerState: str
    id: int
    id64: int
    name: str
    coords: Coordinates
    date: str

    state: Optional[str] = None
    government: Optional[str] = None
    allegiance: Optional[str] = None

    def is_in_influence_range(self, other: "PowerplaySystem") -> Optional[bool]:
        """
        Returns None if this (self) system is not in a valid state (stronghold or fortified) or `other`
        Returns bool of if `other` system is in range otherwise

        Args:
            other (PowerplaySystem): _description_

        Returns:
            Optional[bool]: _description_
        """
        valid_state = self.powerState in ["Fortified", "Stronghold"]
        if not valid_state:
            return None

        influence_range = 20.0 if self.powerState == "Fortified" else 30.0
        return (
            True if self.coords.distance_to(other.coords) <= influence_range else False
        )


@dataclass
class AcquisitionSystemPairing:
    acquiring_system: PowerplaySystem
    unoccupied_system: System
