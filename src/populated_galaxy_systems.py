from typing import Dict, List, Optional

from .db import SystemDB
from .ed_types import PowerplaySystem, System


class PopulatedGalaxySystems:
    cache: Dict[str, System] = {}
    db = SystemDB()

    @staticmethod
    def from_powerplay_system(powerplay_system: PowerplaySystem):
        return PopulatedGalaxySystems.get_system(powerplay_system.name)

    @staticmethod
    def get_system(system_name: str) -> Optional[System]:
        if system_name not in PopulatedGalaxySystems.cache:
            PopulatedGalaxySystems.cache[system_name] = (
                PopulatedGalaxySystems.db.get_system(system_name)
            )

        return PopulatedGalaxySystems.cache[system_name]

    @staticmethod
    def get_systems(system_names: List[str]) -> List[System]:
        systems = []
        for system_name in system_names:
            system = PopulatedGalaxySystems.get_system(system_name)
            if system is not None:
                systems.append(system)
        return systems
