import pathlib
import json
import pprint
from typing import Dict

from ed_types import System
from constants import GALAXY_POPULATED, GALAXY_POPULATED_IN_NK_PP_RANGE
from powerplay_systems import PowerplaySystems
from timer import Timer

class PopulatedGalaxySystems:
    systems_by_name: Dict[str, System] = {}

    def __ensure_raw_data_dump(self):
        if len(self.systems_by_name) == 0:
            self.__load_data_dump(GALAXY_POPULATED)

    def __load_data_dump(self, dump_file: pathlib.Path):
        timer = Timer()

        systems_by_name = {}
        with dump_file.open("r") as f:
            systems = json.load(f)
            for system in systems:
                try:
                    systems_by_name[system["name"]] = System(**system)
                except:
                    pprint.pprint(system, depth=1)
                    raise

        self.systems_by_name = systems_by_name
        timer.end()

    def load_processed_dump_file(self, dump_file: str):
        self.__load_data_dump(dump_file)

    def get_nakato_kaine_systems(self) -> Dict[str, System]:
        timer = Timer()
        with GALAXY_POPULATED_IN_NK_PP_RANGE.open("r") as f:
            data = json.load(f)
            timer.end()

            for system_name, system in data.items():
                try:
                    System(**system)
                except:
                    pprint.pprint(system, depth=1)

            return { system_name: System(**system) for system_name, system in data.items() }

    def filter_and_dump_nakato_kaine_systems(self):
        self.__ensure_raw_data_dump()

        timer = Timer()

        pp_systems = PowerplaySystems.get_powerplay_systems()
        unoccupied_nk_systems_in_boom = pp_systems.get_system_names({
            "power": ["Nakato Kaine"],
            # "powerState": ["Unoccupied"],
            # "state": ["Boom"]
        })

        target_systems = {}
        for system_name, system in self.systems_by_name.items():
            if system_name in unoccupied_nk_systems_in_boom:
                target_systems[system_name] = system

        with GALAXY_POPULATED_IN_NK_PP_RANGE.open("w") as f:
            json.dump(target_systems, f)

        timer.end()

    def get_stations(self, system_name: str):
        if system_name not in self.systems_by_name:
            raise Exception(f"Tried querying for '{system_name}' but PopulatedGalaxySystems didn't know about that system!")
        return self.systems_by_name[system_name].stations