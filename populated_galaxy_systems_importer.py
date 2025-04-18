import json
import pprint
from typing import Dict, List, Optional

from db import SystemDB
from ed_types import System
from powerplay_systems import PowerplaySystems
from timer import Timer
from pathlib import Path


class PopulatedGalaxySystemsImporter:
    systems_by_name: Dict[str, System] = {}
    pp_systems: PowerplaySystems

    def __init__(self, dump_file: Path, dump_is_processed=False):
        self.__load_data_dump(dump_file, dump_is_processed)
        self.pp_systems = PowerplaySystems.get_powerplay_systems()
        self.db = SystemDB()

    def __load_data_dump(self, dump_file: Path, dump_is_processed: bool):
        timer = Timer()

        systems_by_name = {}
        with dump_file.open("r") as f:
            systems = json.load(f)
            if dump_is_processed:
                # If processed, it's already a name-to-system mapping
                systems_by_name = systems
            else:
                # Else, it's a list of system objects from Spansh dumps
                for system in systems:
                    try:
                        systems_by_name[system["name"]] = System.schema().load(system)
                    except:
                        pprint.pprint(system, depth=1)
                        raise

        self.systems_by_name = systems_by_name
        timer.end()

        print("== Loaded Data Dump ==")
        print(f">> {len(self.systems_by_name.keys())} Systems")
        print(
            f">> 'Col 285 Sector WM-N b22-3' loaded: {'YES' if 'Col 285 Sector WM-N b22-3' in self.systems_by_name else 'NO'}"
        )

    def filter_and_import_systems(self, filters: Optional[Dict[str, List[str]]] = None):
        filters = filters if filters is not None else {}
        timer = Timer()

        nk_systems = self.pp_systems.get_system_names(filters)

        for system_name, system in self.systems_by_name.items():
            if system_name in nk_systems or system_name == "HIP 23692":
                self.db.upsert_system(system)

        timer.end()
