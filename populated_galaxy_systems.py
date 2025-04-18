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

    def __load_data_dump(self, dump_file: str):
        p_in = pathlib.Path(dump_file)

        timer = Timer()

        systems_by_name = {}
        with p_in.open("r") as f:
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
        p_out = pathlib.Path(GALAXY_POPULATED_IN_NK_PP_RANGE)
        timer = Timer()
        with p_out.open("r") as f:
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

        p_out = pathlib.Path(GALAXY_POPULATED_IN_NK_PP_RANGE)
        with p_out.open("w") as f:
            json.dump(target_systems, f)

        timer.end()