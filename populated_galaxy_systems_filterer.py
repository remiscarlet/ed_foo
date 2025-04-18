from typing import Dict, List

from ed_types import System, json_dump
from constants import GALAXY_POPULATED_IN_NK_BOOM_UNOCCUPIED_PP_RANGE, GALAXY_POPULATED_IN_NK_PP_RANGE, GALAXY_POPULATED_IN_PP_RANGE
from populated_galaxy_systems import PopulatedGalaxySystemsBase
from timer import Timer
from pathlib import Path

class PopulatedGalaxySystemsFilterer(PopulatedGalaxySystemsBase):
    def filter_and_dump_unoccupied_boom_nakato_kaine_systems(self):
        self.filter_and_dump_systems_by_pp_stats(GALAXY_POPULATED_IN_NK_BOOM_UNOCCUPIED_PP_RANGE, {
            "power": ["Nakato Kaine"],
            "powerState": ["Unoccupied"],
            "state": ["Boom"]
        })

    def filter_and_dump_all_nakato_kaine_systems(self):
        self.filter_and_dump_systems_by_pp_stats(GALAXY_POPULATED_IN_NK_PP_RANGE, {
            "power": ["Nakato Kaine"],
        })

    def filter_and_dump_all_pp_systems(self):
        self.filter_and_dump_systems_by_pp_stats(GALAXY_POPULATED_IN_PP_RANGE, {})

    def filter_and_dump_systems_by_pp_stats(self, output_dump_file: Path, filters: Dict[str, List[str]]):
        timer = Timer()

        nk_systems = self.pp_systems.get_system_names(filters)

        target_systems = {}
        for system_name, system in self.systems_by_name.items():
            if system_name in nk_systems or system_name == "HIP 23692":
                target_systems[system_name] = system

        with output_dump_file.open("w") as f:
            json_dump(target_systems, f)

        timer.end()