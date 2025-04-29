from itertools import batched

from src.adapters.data_ingestion.spansh.adapter import SpanshDataRetrievalAdapter
from src.adapters.persistence.postgresql.adapter import SystemsAdapter
from src.common.timer import Timer

# from src.core.ports.system_port import SystemPort
# from src.core.ports.data_dump_retrieval_port import DataDumpRetrievalPort


CHUNK_SIZE = 10


def import_data_usecase() -> None:
    data_adapter = SpanshDataRetrievalAdapter()
    # data_adapter = DataDumpRetrievalPort()
    # data_adapter.download_data()

    system_adapter = SystemsAdapter()
    # system_adapter = SystemPort()
    for systems_chunk in list(batched(data_adapter.load_data().values(), CHUNK_SIZE)):
        timer = Timer(f"Batching '{CHUNK_SIZE}' items")
        system_adapter.upsert_systems(list(systems_chunk))
        timer.end()
