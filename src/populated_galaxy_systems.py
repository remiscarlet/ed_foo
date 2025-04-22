from pprint import pformat
from typing import Dict, List, Optional

from src.logging import get_logger

from .db import SystemDB
from .types import PowerplaySystem, System

logger = get_logger(__name__)


class PopulatedGalaxySystems:
    cache: Dict[str, System] = {}
    db = SystemDB()

    @staticmethod
    def from_powerplay_system(powerplay_system: PowerplaySystem) -> Optional[System]:
        return PopulatedGalaxySystems.get_system(powerplay_system.name)

    @staticmethod
    def get_system(system_name: str) -> Optional[System]:
        if system_name not in PopulatedGalaxySystems.cache:
            system = PopulatedGalaxySystems.db.get_system(system_name)
            if system is not None:
                PopulatedGalaxySystems.cache[system_name] = system

        return PopulatedGalaxySystems.cache.get(system_name)

    @staticmethod
    def get_systems(system_names: List[str]) -> List[System]:
        logger.debug(pformat({"system_names": system_names}))
        systems = []
        for system_name in system_names:
            system = PopulatedGalaxySystems.get_system(system_name)
            if system is not None:
                systems.append(system)
        return systems
