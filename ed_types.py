from dataclasses import dataclass, is_dataclass
from typing import List, Optional


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


@dataclass
class ControllingFaction:
    allegiance: str
    government: str
    name: str

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

@dataclass
class Timestamps:
    powerState: str
    powers: str

@nested_dataclass
class System:
    allegiance: str
    bodies: List
    bodyCount: int
    controllingFaction: ControllingFaction
    coords: Coordinates
    date: str
    factions: list
    government: str
    id64: int
    name: str
    population: int
    primaryEconomy: str
    secondaryEconomy: str
    security: str
    stations: List

    def distance_from(self, target_system: "System"):
        return self.coords.distance_from(target_system.coords)

    def is_in_powerplay(self):
        return (
            self.powers is not None and
            len(self.powers) > 0
        )

    controllingPower: Optional[str] = None
    powerState: Optional[str] = None
    powers: Optional[List[str]] = None
    powerConflictProgress: Optional[List] = None
    timestamps: Optional[Timestamps] = None

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