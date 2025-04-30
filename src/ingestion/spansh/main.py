import json
from itertools import batched
from pathlib import Path
from pprint import pprint
from typing import Any, Dict, List, Optional

import yaml
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import DeclarativeMeta, Session

from src.adapters.persistence.postgresql import SessionLocal
from src.adapters.persistence.postgresql.db import (
    BodiesDB,
    CommoditiesDB,
    FactionPresencesDB,
    FactionsDB,
    HotspotsDB,
    MarketCommoditiesDB,
    OutfittingShipModulesDB,
    RingsDB,
    ShipModulesDB,
    ShipsDB,
    ShipyardShipsDB,
    SignalsDB,
    StationsDB,
    SystemsDB,
)
from src.common.constants import (
    COMMODITIES_YAML_FMT,
    GALAXY_POPULATED_JSON,
    GALAXY_POPULATED_JSON_GZ,
    GALAXY_POPULATED_JSON_URL,
    METADATA_DIR,
    METADATA_SCHEMAS_DIR,
)
from src.common.logging import get_logger
from src.common.timer import Timer
from src.common.utils import download_file, ungzip
from src.ingestion.spansh.models.system_spansh import SystemSpansh

logger = get_logger(__name__)


def upsert_all[T](
    session: Session,
    model: T,
    rows: List[Dict[str, Any]],
    conflict_cols: list[str],
    exclude_update_cols: list[str] = [],
) -> List[T]:
    if not rows:
        return
    pprint(rows)

    updatable_cols = [
        col.name
        for col in model.__table__.columns
        if col.name not in conflict_cols and col.name not in exclude_update_cols
    ]

    stmt = (
        pg_insert(model)
        .values(rows)
        .on_conflict_do_update(
            index_elements=conflict_cols, set_={col: getattr(pg_insert(model).excluded, col) for col in updatable_cols}
        )
    )

    print(str(stmt))

    rows = session.scalars(stmt.returning(model), execution_options={"populate_existing": True})
    session.commit()

    return rows.all()


class SpanshDataLayerPartitioner:
    """Processes Spansh data dumps into data "layers"

    Data layers are defined as the layers of tables that must be inserted in layer order to adhere to FK relation requirements.
    Ie, cannot insert a row needing an FK if the FK table's row doesn't exist yet.
    """

    layer1 = {
        FactionsDB.__tablename__: {},
        # CommoditiesDB.__tablename__: {},
        # ShipsDB.__tablename__: {},
        # ShipModulesDB.__tablename__: {},
    }
    layer2 = {SystemsDB.__tablename__: {}}
    layer3 = {
        FactionPresencesDB.__tablename__: {},
        BodiesDB.__tablename__: {},
    }
    layer4 = {
        StationsDB.__tablename__: {},
        SignalsDB.__tablename__: {},
        RingsDB.__tablename__: {},
    }
    layer5 = {
        MarketCommoditiesDB.__tablename__: {},
        ShipyardShipsDB.__tablename__: {},
        OutfittingShipModulesDB.__tablename__: {},
        HotspotsDB.__tablename__: {},
    }
    id_cache = {}

    def cache_id(self, entity: Any, id: Any) -> None:
        self.id_cache[hash(entity)] = id

    def get_entity_id(self, entity: Any) -> Optional[Any]:
        return self.id_cache.get(hash(entity))
        # tablename = entity.__tablename__
        # for layer in [self.layer1, self.layer2, self.layer3, self.layer4, self.layer5]:
        #     if tablename in layer:
        #         return layer.get(tablename, {}).get(entity)

    def __init__(self) -> None:
        self.session = SessionLocal()

    def partition_system(self, input_system: SystemSpansh):
        pass

    def insert_systems(self, input_systems: List[SystemSpansh]):
        # Layer 1
        faction_spansh_by_name = {
            faction.name: faction for system in input_systems for faction in system.factions or []
        }
        to_use = ["allegiance", "government", "name"]
        factions_by_name = {}
        for system in input_systems:
            for faction in system.factions or []:
                factions_by_name[faction.name] = {k: v for k, v in faction.to_sqlalchemy_dict().items() if k in to_use}
        faction_rows = upsert_all(self.session, FactionsDB, list(factions_by_name.values()), ["name"], ["id"])
        for row in faction_rows:
            faction_spansh = faction_spansh_by_name.get(row.name)
            self.cache_id(faction_spansh, row.id)

            for system in input_systems:
                if system.controlling_faction and system.controlling_faction.name == row.name:
                    self.id_cache[system.controlling_faction] = row.id

        pprint("!!!!!")
        pprint(faction_rows)
        pprint(self.layer1)

        # Layer 2
        systems_spansh_by_name = {system.name: system for system in input_systems}
        systems = [
            system.to_sqlalchemy_dict(self.get_entity_id(system.controlling_faction)) for system in input_systems
        ]
        # controlling_faction_id = self.get_entity_id(input_system.controlling_faction)
        # system = input_system.to_sqlalchemy_dict(controlling_faction_id)
        system_rows = upsert_all(
            self.session,
            SystemsDB,
            systems,
            ["name"],
            ["id"],
        )
        for row in system_rows:
            spansh_system = systems_spansh_by_name.get(row.name)
            self.cache_id(spansh_system, row.id)

        # Layer 3
        rows = []
        for system in input_systems:
            for faction in system.factions or []:
                system_id = self.get_entity_id(system)
                faction_id = self.get_entity_id(faction)
                rows.append(
                    {
                        "system_id": system_id,
                        "faction_id": faction_id,
                        "state": faction.state,
                        "influence": faction.influence,
                    }
                )
        system_rows = upsert_all(
            self.session,
            FactionPresencesDB,
            rows,
            ["faction_id", "system_id"],
            ["id"],
        )


class SpanshDataPipeline:
    def __init__(self) -> None:
        self.session = SessionLocal()
        self.partitioner = SpanshDataLayerPartitioner()

    def download_data(self) -> None:
        GALAXY_POPULATED_JSON_GZ.parent.mkdir(parents=True, exist_ok=True)

        download_file(GALAXY_POPULATED_JSON_URL, GALAXY_POPULATED_JSON_GZ)
        ungzip(GALAXY_POPULATED_JSON_GZ, GALAXY_POPULATED_JSON)

    def load_metadata_yaml_into_pg(self, path: Path) -> None:
        pprint(f"Inserting '{path}'")

        with open(path, "r") as f:
            dict = yaml.load(f.read(), Loader=yaml.Loader)
            commodities = []
            for name, values in dict.items():
                commodities.append(
                    {
                        "symbol": values.get("symbol", name),
                        "name": name,
                        "category": values.get("category"),
                        "is_mineable": values.get("is_mineable"),
                        "ring_types": values.get("ring_types"),
                        "mining_method": values.get("mining_method"),
                        "has_hotspots": values.get("has_hotspots", False),
                    }
                )

            commodity_rows = upsert_all(self.session, CommoditiesDB, commodities, ["symbol"], [])
            pprint(commodity_rows)

    def load_data(self) -> Dict[str, SystemSpansh]:
        spansh_systems_list: List[SystemSpansh] = []

        timer = Timer("Spansh datadump load")
        with GALAXY_POPULATED_JSON.open("r") as f:
            system_dicts = json.load(f)
            spansh_systems_list = [SystemSpansh.model_validate(system_dict) for system_dict in system_dicts]
        timer.end()

        logger.info("== Loaded Data Dump ==")
        logger.info(f">> {len(spansh_systems_list)} Systems")

        systems_by_name: Dict[str, SystemSpansh] = {}
        for system in spansh_systems_list:
            systems_by_name[system.name] = system

        test_system = "Col 285 Sector WM-N b22-3"
        logger.info(f">> '{test_system}' loaded: {'YES' if test_system in systems_by_name else 'NO'}")

        return systems_by_name

    CHUNK_SIZE = 10

    def run(self) -> None:
        # self.download_data()

        for path in METADATA_DIR.rglob(COMMODITIES_YAML_FMT):
            self.load_metadata_yaml_into_pg(path)

        # system_adapter = SystemPort()
        for systems_chunk in list(batched(self.load_data().values(), self.CHUNK_SIZE)):
            # self.upsert_systems(list(systems_chunk))

            timer = Timer(f"Batching '{self.CHUNK_SIZE}' items")
            self.partitioner.insert_systems(systems_chunk)
            timer.end()

    def upsert_systems(self, systems: List[SystemSpansh]) -> None:
        upsert_all(self.session, SystemsDB, systems, conflict_cols=["id", "name"], exclude_update_cols=[])


if __name__ == "__main__":
    pipeline = SpanshDataPipeline()
    pipeline.run()
