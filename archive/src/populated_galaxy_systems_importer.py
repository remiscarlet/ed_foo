import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.logging import get_logger

from .db import SystemDB
from .powerplay_systems import PowerplaySystems
from .timer import Timer

logger = get_logger(__name__)


class PopulatedGalaxySystemsImporter:
    systems_by_name: Dict[str, Dict[str, Any]] = {}
    pp_systems: PowerplaySystems

    def __init__(self, dump_file: Path):
        self.__load_data_dump(dump_file)
        self.pp_systems = PowerplaySystems()
        self.db = SystemDB()

    def __load_data_dump(self, dump_file: Path) -> None:
        timer = Timer("__load_data_dump()")

        systems_by_name = {}
        with dump_file.open("r") as f:
            systems = json.load(f)
            for system in systems:
                systems_by_name[system["name"]] = system
        self.systems_by_name = systems_by_name

        timer.end()

        test_system = "Col 285 Sector WM-N b22-3"
        logger.info("== Loaded Data Dump ==")
        logger.info(f">> {len(self.systems_by_name.keys())} Systems")
        logger.info(f">> '{test_system}' loaded: {'YES' if test_system in self.systems_by_name else 'NO'}")

    def filter_and_import_systems(self, filters: Optional[Dict[str, List[str]]] = None) -> None:
        filters = filters if filters is not None else {}
        timer = Timer("Outer filter_and_import_systems")

        # nk_systems = self.pp_systems.get_system_names(filters)

        log_every = 5000
        upserted = 0
        inner_timer = Timer("Inner filter_and_import_systems")
        for system_name, system in self.systems_by_name.items():
            # if system_name in nk_systems or system_name == "HIP 23692":
            self.db.upsert_system(system)
            upserted += 1

            if upserted % log_every == 0:
                logger.info(f"Upserted {log_every} systems in {inner_timer.end():.2f} Seconds")
                inner_timer.restart()

        timer.end()
