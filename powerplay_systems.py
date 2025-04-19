import json
import pathlib
from typing import Dict, List, Optional

from constants import POWERPLAY_SYSTEMS
from ed_types import PowerplaySystem
from timer import Timer


class PowerplaySystems:
    systems: Dict[str, PowerplaySystem] = {}

    def __init__(self):
        timer = Timer("PowerplaySystems.__init__()")

        p_in = pathlib.Path(POWERPLAY_SYSTEMS)

        with p_in.open("r") as f:
            system_dicts = json.load(f)
            systems = PowerplaySystem.schema().load(system_dicts, many=True)
            for system in systems:
                self.systems[system.name] = system

        timer.end()

    _instance: Optional["PowerplaySystems"] = None

    @staticmethod
    def get_powerplay_systems():
        if PowerplaySystems._instance is None:
            PowerplaySystems._instance = PowerplaySystems()
        return PowerplaySystems._instance

    def get_systems(self, filters: Optional[Dict[str, List[str]]] = None):
        """
        If filter is supplied, only returns systems that match all conditions
        Each condition checks if the condition value is in the list of values supplied

        Eg, filters = {
            "power": ["Nakato Kaine"],
            "powerState": ["Unoccupied", "Fortified"],
        }
        Returns all systems controlled by NK AND are either Unoccupied OR Fortified
        """
        system_list: List[PowerplaySystem] = []

        for system in self.systems.values():
            valid = True
            for filterKey, filterVals in filters.items():
                if getattr(system, filterKey) not in filterVals:
                    valid = False
            if valid:
                system_list.append(system)

        return system_list

    def get_system_names(self, filters: Optional[Dict[str, List[str]]] = None):
        systems = self.get_systems(filters)
        return [system.name for system in systems]
