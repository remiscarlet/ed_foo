import json
from typing import Dict, List

from src.adapters.data_ingestion.spansh.models.system_spansh import SystemSpansh
from src.common.constants import (
    GALAXY_POPULATED_JSON,
    GALAXY_POPULATED_JSON_GZ,
    GALAXY_POPULATED_JSON_URL,
)
from src.common.logging import get_logger
from src.common.timer import Timer
from src.common.utils import download_file, ungzip
from src.core.models.system_model import System
from src.core.ports.data_dump_retrieval_port import DataDumpRetrievalPort

logger = get_logger(__name__)


class SpanshDataRetrievalAdapter(DataDumpRetrievalPort):
    def download_data(self) -> None:
        GALAXY_POPULATED_JSON_GZ.parent.mkdir(parents=True, exist_ok=True)

        download_file(GALAXY_POPULATED_JSON_URL, GALAXY_POPULATED_JSON_GZ)
        ungzip(GALAXY_POPULATED_JSON_GZ, GALAXY_POPULATED_JSON)

    def load_data(self) -> Dict[str, System]:
        system_dto_list: List[SystemSpansh] = []

        timer = Timer("Spansh datadump load")
        with GALAXY_POPULATED_JSON.open("r") as f:
            system_dicts = json.load(f)
            system_dto_list = [SystemSpansh.model_validate(system_dict) for system_dict in system_dicts]
        timer.end()

        logger.info("== Loaded Data Dump ==")
        logger.info(f">> {len(system_dto_list)} Systems")

        systems_by_name: Dict[str, System] = {}
        timer = Timer("Spansh to Core model conversion")
        for system in system_dto_list:
            systems_by_name[system.name] = system.to_core_model()
        timer.end()

        test_system = "Col 285 Sector WM-N b22-3"
        logger.info(f">> '{test_system}' loaded: {'YES' if test_system in systems_by_name else 'NO'}")

        return systems_by_name
