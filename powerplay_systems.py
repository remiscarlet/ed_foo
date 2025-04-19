import pprint
from typing import Dict, List, Optional

from db import SystemDB
from ed_types import PowerplaySystem


class PowerplaySystems:
    systems: Dict[str, PowerplaySystem] = {}

    def __init__(self):
        self.db = SystemDB()
        self.cache = {}

    def get_acquisition_systems(
        self, power: str, factionStates: Optional[List[str]] = None
    ):
        all_systems = self.db.get_unoccupied_powerplay_systems(power)
        pprint.pprint(
            {
                "power": power,
                "factionStates": factionStates,
                "num_all_systems": len(all_systems),
            }
        )

        if factionStates:
            rtn = [
                system
                for system in all_systems
                if system.controlling_faction_in_states(factionStates)
            ]
            return rtn
        else:
            return all_systems

    def get_reinforcement_systems(
        self,
        power: str,
        powerStates: Optional[List[str]] = None,
        factionStates: Optional[List[str]] = None,
    ):
        all_systems = self.db.get_powerplay_systems(power, powerStates)
        pprint.pprint(
            {
                "power": power,
                "powerStates": powerStates,
                "factionStates": factionStates,
                "num_all_systems": len(all_systems),
            }
        )

        if factionStates:
            rtn = [
                system
                for system in all_systems
                if system.controlling_faction_in_states(factionStates)
            ]
            return rtn
        else:
            return all_systems
