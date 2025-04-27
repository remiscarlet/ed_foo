from adapters.data_ingestion.spansh.loader import load_spansh_populated_systems_dump


def import_data_usecase():
    systems_by_name = load_spansh_populated_systems_dump()
    for system_name, system in systems_by_name.items():
        pass
