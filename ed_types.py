from collections import defaultdict
import dataclasses
import enum
import json
import pprint
from dataclasses_json import config, dataclass_json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class Minerals(enum.Enum):
    Monazite = "Monazite"
    Platinum = "Platinum"


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
    distanceToArrival: Optional[str] = None
    meanAnomaly: Optional[str] = None


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


@dataclass_json
@dataclass
class Asteroids:
    name: str
    type: str
    mass: float
    innerRadius: float
    outerRadius: float

    id64: Optional[int] = None
    signals: Optional[Dict[str, Any]] = None

    def extract_signals(self) -> Dict[Minerals, int]:
        if not getattr(self, "signals"):
            return {}
        return self.signals.get("signals", {})

    def is_invalid_ring_for_mineral(self, mineral: Minerals) -> bool:
        return mineral is Minerals.Platinum and self.type != "Metallic"


@dataclass_json
@dataclass
class Body:
    id64: int
    bodyId: int
    name: str
    stations: List[Station]
    updateTime: str

    absoluteMagnitude: Optional[float] = None
    age: Optional[int] = None
    argOfPeriapsis: Optional[float] = None
    ascendingNode: Optional[float] = None
    atmosphereComposition: Optional[Dict[str, Any]] = None
    atmosphereType: Optional[str] = None
    axialTilt: Optional[float] = None
    belts: Optional[List[Asteroids]] = None
    distanceToArrival: Optional[float] = None
    earthMasses: Optional[float] = None
    gravity: Optional[float] = None
    isLandable: Optional[bool] = None
    luminosity: Optional[str] = None
    mainStar: Optional[bool] = None
    materials: Optional[Dict[str, Any]] = None
    meanAnomaly: Optional[float] = None
    orbitalEccentricity: Optional[float] = None
    orbitalInclination: Optional[float] = None
    orbitalPeriod: Optional[float] = None
    parents: Optional[List[Dict[str, int]]] = None
    radius: Optional[float] = None
    reserveLevel: Optional[str] = None
    rings: Optional[List[Asteroids]] = None
    rotationalPeriod: Optional[float] = None
    rotationalPeriodTidallyLocked: Optional[bool] = None
    semiMajorAxis: Optional[float] = None
    signals: Optional[Dict[str, Any]] = None
    solarMasses: Optional[float] = None
    solarRadius: Optional[float] = None
    solidComposition: Optional[Any] = None
    spectralClass: Optional[str] = None
    subType: Optional[str] = None
    surfacePressure: Optional[float] = None
    surfaceTemperature: Optional[float] = None
    terraformingState: Optional[str] = None
    timestamps: Optional[Timestamps] = None
    type: Optional[str] = None
    volcanismType: Optional[str] = None


def _default_serialize(o):
    if hasattr(o, "to_dict"):
        return o.to_dict()
    raise TypeError(f"Type {o!r} not serializable")


@dataclass_json
@dataclass
class System:
    allegiance: str
    bodies: List[Body]
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

    def distance_to(self, target_system: "System"):
        return self.coords.distance_to(target_system.coords)

    def is_in_powerplay(self):
        return self.powers is not None and len(self.powers) > 0

    def get_stations_with_services(self, services: List[str]) -> List[Station]:
        expected_services = set(services)

        stations = []
        for station in self.stations:
            available_services = (
                set() if station.services is None else set(station.services)
            )
            if expected_services.intersection(available_services):
                stations.append(station)

        return stations

    def get_hotspot_rings(self, target_minerals: List[Minerals]):
        """Returns a dict of ring names, minerals, and hotspot counts

        Eg,
        {
            "HIP 80266 6 A Ring": {
                "Monazite": 1
            },
            "HIP 80266 6 B Ring": {
                "Monazite": 1
            }
        }
        """
        if not self.bodies:
            return {}

        # ring_name -> mineral -> count
        hotspots: defaultdict[str, defaultdict[Minerals, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        for body in self.bodies:
            if not body.rings:
                continue

            for ring in body.rings:
                signals = ring.extract_signals()
                if not signals:
                    continue

                for mineral in target_minerals:
                    count = signals.get(mineral.value, 0)
                    if count <= 0:
                        continue
                    if ring.is_invalid_ring_for_mineral(mineral):
                        continue

                    hotspots[ring.name][mineral.value] += count

        # Convert nested defaultdicts back to normal dicts
        return {
            ring: dict(mineral_hotspots) for ring, mineral_hotspots in hotspots.items()
        }

    @staticmethod
    def db_table_name():
        return "system"

    @staticmethod
    def db_column_list():
        cols = [field.name for field in dataclasses.fields(System)]
        return ", ".join(cols)

    @staticmethod
    def db_values_list(system_dict: Dict):
        cols = [field.name for field in dataclasses.fields(System)]
        rtn = ""
        for column_name in cols:
            col_val = system_dict.get(column_name)
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
class PlayerMinorFaction:
    name: str
    influence: float

    government: Optional[str] = None
    allegiance: Optional[str] = None
    state: Optional[str] = None


@dataclass_json
@dataclass
class PowerplaySystem:
    powerState: str
    id64: int
    name: str
    coords: Coordinates
    date: str
    powers: List[str]

    power: Optional[str] = None
    factions: Optional[List[PlayerMinorFaction]] = None

    government: Optional[str] = None
    allegiance: Optional[str] = None

    def controlling_faction_in_states(self, target_states: List[str]):
        controlling_faction = max(self.factions, key=lambda faction: faction.influence)
        return controlling_faction.state in target_states

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
class AcquisitionSystemPairings:
    unoccupied_system: System
    acquiring_systems: List[System]

    def has_valid_hotspot_ring(self, minerals: List[Minerals]):
        for system in self.acquiring_systems:
            if system.get_hotspot_rings(minerals):
                return True
        return False