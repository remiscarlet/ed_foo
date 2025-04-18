from db import SystemDB
from ed_types import PowerplaySystem


class PopulatedGalaxySystems:
    def __init__(self):
        self.db = SystemDB()

    def from_powerplay_system(self, powerplay_system: PowerplaySystem):
        return self.get_system(powerplay_system.name)

    def get_system(self, system_name: str):
        return self.db.get_system(system_name)
