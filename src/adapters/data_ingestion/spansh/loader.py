import json
from pathlib import Path
from threading import Timer
from typing import Dict, List

from adapters.data_ingestion.spansh.models.system_spansh import SystemDTO
from src.common.constants import GALAXY_POPULATED_JSON
from src.common.logging import get_logger
from src.core.models.system_model import System

logger = get_logger(__name__)


def load_system_json_dump(dump_file: Path) -> List[SystemDTO]:
    timer = Timer("__load_data_dump()")

    system_dto_list: List[SystemDTO] = []
    with dump_file.open("r") as f:
        systems_dict = json.load(f)
        system_dto_list = SystemDTO.schema().loads(systems_dict, many=True)

    timer.end()

    logger.info("== Loaded Data Dump ==")
    logger.info(f">> {len(system_dto_list)} Systems")

    return system_dto_list


def load_spansh_populated_systems_dump() -> Dict[str, System]:
    dump_file = GALAXY_POPULATED_JSON
    system_dto_list: List[SystemDTO] = load_system_json_dump(dump_file)

    systems_by_name: Dict[str, System] = {}
    for system in system_dto_list:
        systems_by_name[system.name] = system.to_core_system()

    test_system = "Col 285 Sector WM-N b22-3"
    logger.info(f">> '{test_system}' loaded: {'YES' if test_system in systems_by_name else 'NO'}")

    return systems_by_name
