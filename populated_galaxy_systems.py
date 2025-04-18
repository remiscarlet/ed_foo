import pprint
from typing import Dict

from ed_types import System, json_load, json_dump
from constants import GALAXY_POPULATED_IN_NK_PP_RANGE
from powerplay_systems import PowerplaySystems
from timer import Timer
from pathlib import Path

class PopulatedGalaxySystemsBase:
    systems_by_name: Dict[str, System] = {}
    pp_systems: PowerplaySystems

    def __init__(self, dump_file: Path, dump_is_processed = False):
        self.__load_data_dump(dump_file, dump_is_processed)
        self.pp_systems = PowerplaySystems.get_powerplay_systems()

    def __load_data_dump(self, dump_file: Path, dump_is_processed: bool):
        timer = Timer()

        systems_by_name = {}
        with dump_file.open("r") as f:
            systems = json_load(f)
            if dump_is_processed:
                # If processed, it's already a name-to-system mapping
                systems_by_name = systems
            else:
                # Else, it's a list of system objects from Spansh dumps
                for system in systems:
                    try:
                        systems_by_name[system["name"]] = System(**system)
                    except:
                        pprint.pprint(system, depth=1)
                        raise

        self.systems_by_name = systems_by_name
        timer.end()

        print("== Loaded Data Dump ==")
        print(f">> {len(self.systems_by_name.keys())} Systems")
        print(f">> 'Col 285 Sector WM-N b22-3' loaded: {'YES' if 'Col 285 Sector WM-N b22-3' in self.systems_by_name else 'NO'}")

class PopulatedGalaxySystems(PopulatedGalaxySystemsBase):
    def get_system(self, system_name: str):
        if system_name not in self.systems_by_name:
            raise Exception(f"Tried querying for '{system_name}' but PopulatedGalaxySystems didn't know about that system!")

        return self.systems_by_name[system_name]