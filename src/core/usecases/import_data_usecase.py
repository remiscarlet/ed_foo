from src.adapters.data_ingestion.spansh.data_ingestor import SpanshDataIngestor
from src.adapters.data_ingestion.spansh.loader import load_spansh_populated_systems_dump


def import_data_usecase() -> None:
    ingestor = SpanshDataIngestor()
    for system_name, system in ingestor.get_systems().items():
        pass
