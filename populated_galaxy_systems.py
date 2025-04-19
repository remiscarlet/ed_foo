from typing import Dict, List, Optional
from db import SystemDB
from ed_types import PowerplaySystem


class PopulatedGalaxySystems:
    def __init__(self):
        self.db = SystemDB()
        self.cache = {}

    def from_powerplay_system(self, powerplay_system: PowerplaySystem):
        return self.get_system(powerplay_system.name)

    def get_system(self, system_name: str):
        if system_name not in self.cache:
            self.cache[system_name] = self.db.get_system(system_name)

        return self.cache[system_name]

    def get_systems(self, system_names: List[str]):
        systems = []
        for system_name in system_names:
            systems.append(self.get_system(system_name))
        return systems
