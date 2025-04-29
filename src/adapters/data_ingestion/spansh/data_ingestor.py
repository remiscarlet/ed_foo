from typing import Any, Dict

from src.adapters.data_ingestion.spansh.loader import load_spansh_populated_systems_dump
from src.core.ports.data_ingestion_port import DataIngestionPort


class SpanshDataIngestor(DataIngestionPort):
    def get_systems(self) -> Dict[str, Any]:
        return load_spansh_populated_systems_dump()
