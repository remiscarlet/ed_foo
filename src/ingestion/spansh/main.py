import json
from itertools import batched
from pathlib import Path
from pprint import pformat, pprint
from typing import Any, Dict, List, Optional, Type, cast

import yaml
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from src.adapters.persistence.postgresql import BaseModel, SessionLocal
from src.adapters.persistence.postgresql.db import (
    BodiesDB,
    CommoditiesDB,
    FactionPresencesDB,
    FactionsDB,
    RingsDB,
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
)
from src.common.logging import get_logger
from src.common.timer import Timer
from src.common.utils import download_file, ungzip
from src.ingestion.spansh.models.system_spansh import SystemSpansh

logger = get_logger(__name__)


def upsert_all[T: BaseModel](
    session: Session,
    model: Type[T],
    rows: List[Dict[str, Any]],
    conflict_cols: list[str],
    exclude_update_cols: list[str] = [],
) -> List[T]:
    if not rows:
        return []
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

    results = session.scalars(stmt.returning(model), execution_options={"populate_existing": True})
    session.commit()

    return list(iter(results.all()))


class SpanshDataLayerPartitioner:
    """Processes Spansh data dumps into data "layers"

    Data layers are defined as the layers of tables that
    must be inserted in layer order to adhere to FK relation requirements.
    Ie, cannot insert a row needing an FK if the FK table's row doesn't exist yet.

    Layer 1:
      - FactionsDB
        - Used in SystemsDB.controlling_faction_id
      - CommoditiesDB, ShipsDB, and ShipModulesDB too technically
        - However, they get loaded as metadata in load_metadata_yaml_into_pg()
        - Used in MarketCommoditiesDB.commodity_sym, ShipsDB.ship_id, ShipModulesDB.module_id
    Layer 2:
      - SystemsDB (Use)
        - Used in FactionPresencesDB.system_id, BodiesDB.system_id, etc
    Layer 3:
      - FactionPresencesDB
      - BodiesDB
        - Used in StationsDB.owner_id, SignalsDB.body_id, RingsDB.body_id
    Layer 4:
      - StationsDB
        - Used in MarketCommoditiesDB.station_id, ShipyardShipsDB.station_id, OutfittingShipModulesDB.station_id
      - SignalsDB
      - RingsDB
        - Used in HotspotsDB.ring_id
    Layer 5:
      - MarketCommoditiesDB
      - ShipyardShipsDB
      - OutfittingShipModulesDB
      - HotspotsDB

    """

    def __init__(self) -> None:
        self.session = SessionLocal()

    id_cache: Dict[int, int] = {}

    def cache_id(self, entity: Any, id: int) -> None:
        self.id_cache[hash(entity)] = id

    def get_entity_id(self, entity: Any) -> int:
        entity_id = self.id_cache.get(hash(entity))
        if entity_id is None:
            logger.warning(pformat(entity))
            raise Exception("Got an entity that didn't have a cached entity id!")
        return entity_id

    def insert_layer1(self, input_systems: List[SystemSpansh]) -> None:
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
                    self.cache_id(system.controlling_faction, row.id)

        pprint("!!!!!")
        pprint(faction_rows)

    def insert_layer2(self, input_systems: List[SystemSpansh]) -> None:
        # Layer 2
        systems_spansh_by_name = {system.name: system for system in input_systems}
        systems = []
        for system in input_systems:
            controlling_faction_id = self.get_entity_id(system.controlling_faction)
            if controlling_faction_id is None:
                continue
            systems.append(system.to_sqlalchemy_dict(controlling_faction_id=controlling_faction_id))
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

        pprint("!!!!!")
        pprint(system_rows)

    def insert_layer3(self, input_systems: List[SystemSpansh]) -> None:
        # Layer 3 - Faction Presences
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
        faction_presence_rows = upsert_all(
            self.session,
            FactionPresencesDB,
            rows,
            ["faction_id", "system_id"],
            ["id"],
        )

        pprint("!!!!!")
        pprint(faction_presence_rows)

        # Layer 3 - Bodies
        rows = []
        body_by_name = {}
        for system in input_systems:
            system_id = self.get_entity_id(system)
            for body in system.bodies or []:
                rows.append(body.to_sqlalchemy_dict(system_id))
                body_by_name[body.name] = body
        bodies_rows = upsert_all(
            self.session,
            BodiesDB,
            rows,
            ["name"],
            ["id"],
        )
        for row in bodies_rows:
            spansh_body = body_by_name.get(row.name)
            self.cache_id(spansh_body, row.id)

    def insert_layer4(self, input_systems: List[SystemSpansh]) -> None:
        # Layer 4 - Stations
        rows = []
        stations_by_name = {}
        for system in input_systems:
            system_id = self.get_entity_id(system)
            for station in system.stations or []:
                rows.append(station.to_sqlalchemy_dict(system_id, "system"))
                stations_by_name[station.name] = station
            for body in system.bodies or []:
                for station in body.stations or []:
                    rows.append(station.to_sqlalchemy_dict(system_id, "body"))
                    stations_by_name[station.name] = station

        stations_rows = upsert_all(
            self.session,
            StationsDB,
            rows,
            ["name", "owner_id"],
            ["id"],
        )
        for row in stations_rows:
            spansh_station = stations_by_name.get(row.name)
            self.cache_id(spansh_station, row.id)

        # Layer 4 - Signals
        rows = []
        for system in input_systems:
            for body in system.bodies or []:
                body_id = self.get_entity_id(body)
                if body.signals:
                    rows.extend(body.signals.to_sqlalchemy_dicts(body_id))

        upsert_all(
            self.session,
            SignalsDB,
            rows,
            ["body_id", "signal_type"],
            ["id"],
        )

        # Layer 4 - Rings
        rows = []
        for system in input_systems:
            for body in system.bodies or []:
                body_id = self.get_entity_id(body)
                if body_id is None:
                    logger.warning(f"Got a body that didn't have a cached entity id!")
                    logger.warning(pformat(body))
                    continue

                for ring in body.rings or []:
                    rows.append(ring.to_sqlalchemy_dict(body_id))

        upsert_all(
            self.session,
            RingsDB,
            rows,
            ["body_id", "name"],
            ["id"],
        )

    def insert_systems(self, input_systems: List[SystemSpansh]) -> None:
        self.insert_layer1(input_systems)
        self.insert_layer2(input_systems)
        self.insert_layer3(input_systems)
        self.insert_layer4(input_systems)
        # self.insert_layer5(input_systems)


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
            self.partitioner.insert_systems(list(systems_chunk))
            timer.end()


if __name__ == "__main__":
    pipeline = SpanshDataPipeline()
    pipeline.run()
