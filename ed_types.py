import json
from marshmallow.exceptions import ValidationError
from dataclasses_json import config, dataclass_json
from dataclasses import dataclass, field, is_dataclass
from typing import Any, Dict, List, Optional
from functools import partial

CLASS_REGISTRY: dict[str, type] = {}
def register(cls):
    CLASS_REGISTRY[cls.__name__] = cls
    return cls

def default_serialize(o: Any):
    if hasattr(o, "to_dict"):
        d = o.to_dict()
        d["__type__"] = o.__class__.__name__
        return d
    raise TypeError(f"Type {o!r} not serializable")

def deserialize_hook(dct: Dict):
    type_name = dct.pop("__type__", None)
    if not type_name:
        return dct
    cls = CLASS_REGISTRY.get(type_name)
    if not cls:
        return dct

    try:
        return cls.schema().load(dct)
    except ValidationError as err:
        pass
        # 1) See the overall error map
        print("Error map:", err.messages)
        # 2) See what actually got through
        # print("Valid up to error:", err.valid_data)


json_dump = partial(json.dump, default=default_serialize)
json_load = partial(json.load, object_hook=deserialize_hook)


# decorator to wrap original __init__
def nested_dataclass(*args, **kwargs):
    def wrapper(check_class):
        # passing class to investigate
        check_class = dataclass(check_class, **kwargs)
        o_init = check_class.__init__

        def __init__(self, *args, **kwargs):

            for name, value in kwargs.items():

                # getting field type
                ft = check_class.__annotations__.get(name, None)

                if is_dataclass(ft) and isinstance(value, dict):
                    obj = ft(**value)
                    kwargs[name]= obj
                o_init(self, *args, **kwargs)
        check_class.__init__=__init__

        return check_class

    return wrapper(args[0]) if args else wrapper

@register
@dataclass_json
@dataclass
class ControllingFaction:
    allegiance: Optional[str] = None
    government: Optional[str] = None
    name: Optional[str] = None

@register
@dataclass_json
@dataclass
class Coordinates:
    x: float
    y: float
    z: float

    def distance_from(self, other: "Coordinates") -> float:
        dx = (self.x - other.x) ** 2
        dy = (self.y - other.y) ** 2
        dz = (self.z - other.z) ** 2
        return (dx + dy + dz) ** (0.5)

@register
@dataclass_json
@dataclass
class Timestamps:
    powerState: str
    powers: str

@dataclass
class CommodityPriceAndDemand:
    buyPrice: int
    demand: int
    sellPrice: int
    supply: int

@register
@dataclass_json
@nested_dataclass
class Commodity(CommodityPriceAndDemand):
    category: str
    commodityId: int
    name: str
    symbol: str

@register
@dataclass_json
@nested_dataclass
class Market:
    commodities: List[Commodity]
    prohibitedCommodities: List[str]
    updateTime: str

@register
@dataclass_json
@nested_dataclass
class ShipModule:
    category: str
    cls: int = field(metadata=config(field_name="class"))
    moduleId: int
    name: str
    rating: str
    symbol: str

    ship: Optional[str] = None

@register
@dataclass_json
@nested_dataclass
class Outfitting:
    modules: List[ShipModule]
    updateTime: str

@register
@dataclass_json
@nested_dataclass
class Ship:
    name: str
    shipId: int
    symbol: str

@register
@dataclass_json
@nested_dataclass
class Shipyard:
    ships: List[Ship]
    updateTime: str

@register
@dataclass_json
@nested_dataclass
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

    def has_commodities(self, target_commodity_names: List[str], require_all = True):
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

    def get_commodity_price(self, target_commodity_name: str) -> Optional[CommodityPriceAndDemand]:
        if self.market is None:
            return False
        if not self.market.commodities:
            return False

        for commodity in self.market.commodities:
            if commodity.name == target_commodity_name:
                return CommodityPriceAndDemand(commodity.buyPrice, commodity.demand, commodity.sellPrice, commodity.supply)

        return None



@register
@dataclass_json
@nested_dataclass
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

    def distance_from(self, target_system: "System"):
        return self.coords.distance_from(target_system.coords)

    def is_in_powerplay(self):
        return (
            self.powers is not None and
            len(self.powers) > 0
        )

    def get_stations_with_services(self, services: List[str]) -> List[Station]:
        expected_services = set(services)

        stations = []
        for station in self.stations:
            available_services = (
                set()
                if station.services is None
                else set(station.services)
            )
            if expected_services.intersection(available_services):
                stations.append(station)

        return stations

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

@register
@dataclass_json
@nested_dataclass
class PowerplaySystem:
    power: str
    powerState: str
    id: int
    id64: int
    name: str
    coords: Coordinates
    allegiance: str
    government: str
    state: str
    date: str

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

        if isinstance(self.coords, Coordinates):
            self_coords = self.coords
        else:
            self_coords = Coordinates(**self.coords)

        if isinstance(other.coords, Coordinates):
            other_coords = other.coords
        else:
            other_coords = Coordinates(**other.coords)

        influence_range = 20.0 if self.powerState == "Fortified" else 30.0
        in_range = (
            True
            if self_coords.distance_from(other_coords) <= influence_range
            else False
        )

        return in_range