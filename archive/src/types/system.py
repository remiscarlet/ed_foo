import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field, fields
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from dataclasses_json import DataClassJsonMixin, config, dataclass_json

from src.logging import get_logger
from src.types import (
    CommodityPrice,
    Coordinates,
    HasMineableMetadata,
    MineableSymbols,
    MiningMethod,
    RingType,
    Station,
    Timestamps,
    _default_serialize,
)
from src.types.commodities import CommodityCategory
from src.types.station import Commodity
from src.utils import TopNStack

logger = get_logger(__name__)


@dataclass_json
@dataclass
class PlayerMinorFaction(DataClassJsonMixin):
    name: str
    influence: float

    government: Optional[str] = None
    allegiance: Optional[str] = None
    state: Optional[str] = None


@dataclass_json
@dataclass
class ControllingFaction(DataClassJsonMixin):
    allegiance: Optional[str] = None
    government: Optional[str] = None
    name: Optional[str] = None


@dataclass_json
@dataclass
class Signals:
    signals: Dict[MineableSymbols, int]
    updateTime: Optional[datetime] = None


@dataclass_json
@dataclass
class Asteroids(DataClassJsonMixin):
    name: str
    type: str
    mass: float
    innerRadius: float
    outerRadius: float

    id64: Optional[int] = None
    signals: Optional[Signals] = None

    def extract_signals(self) -> Dict[MineableSymbols, int]:
        if self.signals is None:
            return {}
        return self.signals.signals

    def is_invalid_ring_type(self, mineral: HasMineableMetadata) -> bool:
        return RingType(self.type) not in mineral.ring_types


@dataclass_json
@dataclass
class Body(DataClassJsonMixin):
    id64: int
    bodyId: int
    name: str
    stations: List[Station]
    updateTime: datetime

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

    def is_invalid_reserve_level(self, mineable: HasMineableMetadata) -> bool:
        if MiningMethod.CORE_MINING in mineable.mining_methods:
            return False
        elif MiningMethod.LASER_MINING in mineable.mining_methods:
            return self.reserveLevel != "Pristine"
        else:
            raise Exception(f"Got mineral with unknown mining method: '{mineable}'!")


@dataclass_json
@dataclass
class System(DataClassJsonMixin):
    allegiance: str
    bodies: List[Body]
    controllingFaction: ControllingFaction
    coords: Coordinates
    date: datetime = field(
        metadata=config(
            decoder=datetime.fromisoformat,
            encoder=datetime.isoformat,
        )
    )
    factions: List[PlayerMinorFaction]
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

    def distance_to(self, target_system: "System") -> float:
        return self.coords.distance_to(target_system.coords)

    def is_in_powerplay(self) -> bool:
        return self.powers is not None and len(self.powers) > 0

    def get_stations_with_services(self, services: List[str]) -> List[Station]:
        expected_services = set(services)

        stations = []
        for station in self.stations:
            available_services = set() if station.services is None else set(station.services)
            if expected_services.intersection(available_services):
                stations.append(station)

        return stations

    def get_hotspot_rings(
        self, target_mineables: Optional[List[HasMineableMetadata]] = None
    ) -> Dict[str, Dict[HasMineableMetadata, int]]:
        """Returns a dict of ring names, mineables, and hotspot counts

        Tests validity of ringType/reserveLevel per mineable commodity type

        If no `target_mineables` is provided, returns all hotspots.

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

        # ring_name -> mineable -> count
        hotspots: Dict[str, Counter[HasMineableMetadata]] = defaultdict(Counter)

        for body in self.bodies or []:
            for ring in body.rings or []:
                signals = ring.extract_signals()
                if not signals:
                    continue

                mineables = (
                    target_mineables if target_mineables is not None else [sym.getMineableMetadata() for sym in signals]
                )

                for m in mineables:
                    count = signals.get(MineableSymbols(m.symbol), 0)
                    if not count:
                        continue
                    if body.is_invalid_reserve_level(m):
                        continue
                    if ring.is_invalid_ring_type(m):
                        continue

                    hotspots[ring.name][m] += count

        return {ring: dict(mineral_hotspots) for ring, mineral_hotspots in hotspots.items()}

    def get_commodities_prices(self, target_commodities: List[str]) -> Dict[str, Dict[str, CommodityPrice]]:
        # station name -> commodity name -> price
        station_to_commodity_prices: Dict[str, Dict[str, CommodityPrice]] = defaultdict(lambda: {})
        for station in self.stations:
            for commodity in target_commodities:
                price = station.get_commodity_price(commodity)
                if price is None:
                    continue
                if station.market is None:
                    continue

                price.updateTime = station.market.updateTime
                station_to_commodity_prices[station.name][commodity] = price

        return {station: dict(prices) for station, prices in station_to_commodity_prices.items()}

    def get_top_commodity_prices_per_station(
        self,
        top_n: int,
        return_buy_prices: bool,
        min_supply_demand: int,
        station_name: Optional[str] = None,
        category_filter: Optional[List[CommodityCategory]] = None,
        max_data_age_days: Optional[int] = None,
    ) -> Dict[str, TopNStack[Commodity]]:
        """If `station` is provided, filters results to just that station, if it exists in this system."""
        top_by_station: Dict[str, TopNStack[Commodity]] = {}

        stations = [*self.stations]
        for body in self.bodies:
            stations.extend(body.stations)

        for station in stations:
            logger.debug(station.name)
            if station_name is not None and station.name != station_name:
                continue
            if max_data_age_days is not None and (datetime.now(timezone.utc) - station.updateTime) > timedelta(
                days=max_data_age_days
            ):
                continue

            top_n_stack = station.get_top_commodity_prices(top_n, return_buy_prices, min_supply_demand, category_filter)
            logger.debug(top_n_stack)

            if not top_n_stack.is_empty():
                top_by_station[station.name] = top_n_stack

        return top_by_station

    @staticmethod
    def db_table_name() -> str:
        return "system"

    @staticmethod
    def db_column_list() -> str:
        cols = [field.name for field in fields(System)]
        return ", ".join(cols)

    @staticmethod
    def db_values_list(sys_dict: Dict[str, Any]) -> str:
        cols = [field.name for field in fields(System)]
        rtn = ""
        for column_name in cols:
            col_val = sys_dict.get(column_name)
            if col_val is None:
                rtn += "    null,\n"
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
class PowerplaySystem(DataClassJsonMixin):
    """Represents a "lightweight view" of a system with powerplay-specific information

    This avoids needing to pull the heavy station/body data for this system.

    Likely will be deprecated once/if an overall better querying system is implemented with partial data hydration

    Returns:
        _type_: _description_
    """

    powerState: str
    id64: int
    name: str
    coords: Coordinates
    date: datetime = field(
        metadata=config(
            decoder=datetime.fromisoformat,
            encoder=datetime.isoformat,
        )
    )
    powers: List[str]

    power: Optional[str] = None
    factions: Optional[List[PlayerMinorFaction]] = None

    government: Optional[str] = None
    allegiance: Optional[str] = None

    def controlling_faction_in_states(self, target_states: List[str]) -> bool:
        controlling_faction = max(self.factions or [], key=lambda faction: faction.influence)
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
        return True if self.coords.distance_to(other.coords) <= influence_range else False


@dataclass
class AcquisitionSystemPairings:
    unoccupied_system: System
    acquiring_systems: List[System]

    def has_valid_hotspot_ring(self, mineables: List[HasMineableMetadata]) -> bool:
        for system in self.acquiring_systems:
            if system.get_hotspot_rings(mineables):
                return True
        return False
