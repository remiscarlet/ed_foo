import logging
from pathlib import Path
from pprint import pformat
from typing import Any, Callable, Dict, Iterable, List, Type, Union

import ijson  # type: ignore
import yaml
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from src.adapters.persistence.postgresql import BaseModel, BaseModelWithId, SessionLocal
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
)
from src.common.logging import configure_logger, get_logger
from src.common.timer import Timer
from src.common.utils import download_file, seconds_to_str, ungzip
from src.ingestion.spansh.models import BaseSpanshModel
from src.ingestion.spansh.models.body_spansh import AsteroidsSpansh, BodySpansh
from src.ingestion.spansh.models.station_spansh import CommoditySpansh, StationSpansh
from src.ingestion.spansh.models.system_spansh import (
    ControllingFactionSpansh,
    FactionSpansh,
    SystemSpansh,
)

logger = get_logger(__name__)


def upsert_all[T: BaseModel](
    session: Session,
    model: Type[T],
    rows: List[Dict[str, Any]],
    conflict_cols: List[str],
    exclude_update_cols: List[str] = [],
    debug_print_extra_cols: List[str] = [],
) -> List[T]:
    if not rows:
        return []

    cols_to_print = conflict_cols + debug_print_extra_cols
    logger.debug(repr([{k: v for k, v in item.items() if k in cols_to_print} for item in rows]))

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

    logger.trace(str(stmt))

    results = session.scalars(stmt.returning(model), execution_options={"populate_existing": True})
    session.commit()

    return list(iter(results.all()))


def insert_layer1(partitioner: "SpanshDataLayerPartitioner", input_systems: List[SystemSpansh]) -> None:
    logger.info("Layer 1: Factions")

    all_factions: dict[str, Union[FactionSpansh, ControllingFactionSpansh]] = {}
    faction_dicts: dict[str, dict[str, Any]] = {}

    for system in input_systems:
        for faction in system.factions or []:
            all_factions[faction.name] = faction
            faction_dicts[faction.name] = {
                k: v for k, v in faction.to_sqlalchemy_dict().items() if k in ["allegiance", "government", "name"]
            }

        controlling = system.controlling_faction
        if controlling:
            all_factions[controlling.name] = controlling
            faction_dicts[controlling.name] = {
                k: v for k, v in controlling.to_sqlalchemy_dict().items() if k in ["allegiance", "government", "name"]
            }

    faction_objects = upsert_all(partitioner.session, FactionsDB, list(faction_dicts.values()), ["name"], ["id"])
    for faction_obj in faction_objects:
        spansh_faction = all_factions.get(faction_obj.name)
        if spansh_faction is None:
            raise Exception(f"Missing faction '{faction_obj.name}' in original Spansh data.")
        partitioner.cache_spansh_entity_id(spansh_faction, faction_obj.id)


def insert_layer2(partitioner: "SpanshDataLayerPartitioner", input_systems: List[SystemSpansh]) -> None:
    logger.info("Layer 2: Systems")

    systems = []
    system_by_key: Dict[int, SystemSpansh] = {}

    for system in input_systems:
        system_by_key[system.to_cache_key()] = system
        controlling_id = (
            partitioner.get_spansh_entity_id(system.controlling_faction) if system.controlling_faction else None
        )
        systems.append(system.to_sqlalchemy_dict(controlling_faction_id=controlling_id))

    system_objects = upsert_all(partitioner.session, SystemsDB, systems, ["name"], ["id"])

    for system_obj in system_objects:
        original = system_by_key.get(system_obj.to_cache_key())
        if original is None:
            raise Exception(f"Spansh system not found for DB system '{system_obj.to_cache_key_tuple()}'")
        partitioner.cache_spansh_entity_id(original, system_obj.id)


def insert_layer3(partitioner: "SpanshDataLayerPartitioner", input_systems: List[SystemSpansh]) -> None:
    logger.info("Layer 3: FactionPresences and Bodies")

    # --- FactionPresences ---
    presence_rows = []
    for system in input_systems:
        system_id = partitioner.get_spansh_entity_id(system)
        for faction in system.factions or []:
            faction_id = partitioner.get_spansh_entity_id(faction)
            presence_rows.append(
                {
                    "system_id": system_id,
                    "faction_id": faction_id,
                    "state": faction.state,
                    "influence": faction.influence,
                }
            )

    upsert_all(partitioner.session, FactionPresencesDB, presence_rows, ["faction_id", "system_id"], ["id"])

    # --- Bodies ---
    body_rows = []
    spansh_body_by_key: dict[int, BodySpansh] = {}
    for system in input_systems:
        system_id = partitioner.get_spansh_entity_id(system)
        for body in system.bodies or []:
            spansh_body_by_key[body.to_cache_key()] = body
            body_rows.append(body.to_sqlalchemy_dict(system_id))

    body_objects = upsert_all(
        partitioner.session,
        BodiesDB,
        body_rows,
        ["system_id", "name", "type", "sub_type", "body_id", "main_star"],
        ["id"],
    )

    for body_obj in body_objects:
        spansh_body = spansh_body_by_key.get(body_obj.to_cache_key())
        if spansh_body is None:
            raise Exception(f"Body not found in spansh cache for: {pformat(body_obj.to_cache_key_tuple())}")
        partitioner.cache_spansh_entity_id(spansh_body, body_obj.id)


def insert_layer4(partitioner: "SpanshDataLayerPartitioner", input_systems: List[SystemSpansh]) -> None:
    logger.info("Layer 4: Stations, Signals, Rings")

    # --- Stations ---
    rows_by_pk = {}
    stations_by_key: Dict[int, StationSpansh] = {}

    for system in input_systems:
        system_id = partitioner.get_spansh_entity_id(system)

        for station in system.stations or []:
            row = station.to_sqlalchemy_dict(system_id, "system")
            rows_by_pk[(row["name"], row["owner_id"])] = row

            stations_by_key[station.to_cache_key(system_id)] = station

        for body in system.bodies or []:
            body_id = partitioner.get_spansh_entity_id(body)

            for station in body.stations or []:
                row = station.to_sqlalchemy_dict(system_id, "body")
                rows_by_pk[(row["name"], row["owner_id"])] = row

                stations_by_key[station.to_cache_key(system_id)] = station

    station_objects = upsert_all(
        partitioner.session, StationsDB, list(rows_by_pk.values()), ["name", "owner_id"], ["id"]
    )

    for station_obj in station_objects:
        # spansh_station = stations_by_name.get(station_obj.to_cache_key())
        # if spansh_station is None:
        #     raise Exception(f"Missing station: {station_obj.name} - {station_obj.to_cache_key_tuple()}")
        partitioner.cache_spansh_entity_id_by_key(station_obj.to_cache_key(), station_obj.id)

    # --- Signals ---
    signal_rows = []
    for system in input_systems:
        for body in system.bodies or []:
            if body.signals:
                body_id = partitioner.get_spansh_entity_id(body)
                signal_rows.extend(body.signals.to_sqlalchemy_dicts(body_id))

    upsert_all(partitioner.session, SignalsDB, signal_rows, ["body_id", "signal_type"], ["id"])

    # --- Rings ---
    ring_rows = []
    rings_by_key: Dict[int, AsteroidsSpansh] = {}
    for system in input_systems:
        for body in system.bodies or []:
            body_id = partitioner.get_spansh_entity_id(body)
            for ring in body.rings or []:
                ring_rows.append(ring.to_sqlalchemy_dict(body_id))
                rings_by_key[ring.to_cache_key(body_id)] = ring

    ring_objects = upsert_all(partitioner.session, RingsDB, ring_rows, ["body_id", "name"], ["id"])

    for ring_obj in ring_objects:
        spansh_ring = rings_by_key[ring_obj.to_cache_key()]
        if spansh_ring is None:
            raise Exception(f"Missing Ring: {ring_obj.name}")

        spansh_ring_key = spansh_ring.to_cache_key(ring_obj.body_id)
        partitioner.cache_spansh_entity_id_by_key(spansh_ring_key, ring_obj.id)


def insert_layer5(partitioner: "SpanshDataLayerPartitioner", input_systems: List[SystemSpansh]) -> None:
    logger.info("Layer 4: Market, Outfitting, Shipyard, Hotspots")

    # --- Market ---

    commodities: List[Dict[str, Any]] = []

    def extract_commodities(system: SystemSpansh, station: StationSpansh) -> None:
        if station.market is None:
            return
        system_id = partitioner.get_spansh_entity_id(system)
        station_id = partitioner.get_spansh_entity_id_by_key(station.to_cache_key(system_id))

        for commodity in station.market.commodities or []:
            commodities.append(commodity.to_sqlalchemy_dict(station_id, commodity.symbol))

        names: set[str] = set()
        for commodity_name in station.market.prohibited_commodities or []:
            if commodity_name in ["Narcotics"]:
                # Prohibited list can either be commodity _name_ or some category names
                names.update(list(partitioner.get_commodity_names_by_category(commodity_name)))
            else:
                names.add(commodity_name)

        for commodity_name in names:
            commodity_obj = partitioner.get_metadata_by_name(commodity_name)
            if commodity_obj is None:
                raise RuntimeError(f"Got a commodity we didn't know about! '{commodity_name}'")
            commodities.append(CommoditySpansh.to_blacklisted_sqlalchemy_dict(station_id, commodity_obj.symbol))

    for system in input_systems:
        for station in system.stations or []:
            extract_commodities(system, station)
        for body in system.bodies or []:
            for station in body.stations:
                extract_commodities(system, station)

    upsert_all(
        partitioner.session,
        MarketCommoditiesDB,
        commodities,
        ["station_id", "commodity_sym", "is_blacklisted"],
        ["id"],
        ["buy_price"],
    )

    # --- Outfitting ---
    modules: List[Dict[str, Any]] = []

    def extract_modules(system: SystemSpansh, station: StationSpansh) -> None:
        if station.outfitting is None:
            return
        system_id = partitioner.get_spansh_entity_id(system)
        station_id = partitioner.get_spansh_entity_id_by_key(station.to_cache_key(system_id))  # noqa: F841
        # TODO: Import module metadata first
        # for module in station.outfitting.modules:
        #     module_id = partitioner.get_metadata_by_name(module.symbol)
        #     modules.append(module.to_sqlalchemy_dict(station_id, module_id))

    for system in input_systems:
        for station in system.stations or []:
            extract_modules(system, station)
        for body in system.bodies or []:
            for station in body.stations:
                extract_modules(system, station)

    upsert_all(partitioner.session, OutfittingShipModulesDB, modules, ["station_id", "module_id"], ["id"])

    # --- Shipyard ---
    ships: List[Dict[str, Any]] = []

    def extract_ships(system: SystemSpansh, station: StationSpansh) -> None:
        if station.outfitting is None:
            return
        system_id = partitioner.get_spansh_entity_id(system)
        station_id = partitioner.get_spansh_entity_id_by_key(station.to_cache_key(system_id))  # noqa: F841
        # for ship in station.shipyard.ships:
        #     ship_id = partitioner.get_metadata_by_name(ship.symbol)
        #     ships.append(ship.to_sqlalchemy_dict(station_id, ship_id))

    for system in input_systems:
        for station in system.stations or []:
            extract_ships(system, station)
        for body in system.bodies or []:
            for station in body.stations:
                extract_ships(system, station)

    upsert_all(partitioner.session, ShipyardShipsDB, ships, ["station_id", "ship_id"], ["id"])

    # --- Hotspots ---
    hotspots = []
    for system in input_systems:
        for body in system.bodies or []:
            if body.rings is None:
                continue

            body_id = partitioner.get_spansh_entity_id_by_key(body.to_cache_key())

            for ring in body.rings:
                if ring.signals is None:
                    continue
                ring_id = partitioner.get_spansh_entity_id_by_key(ring.to_cache_key(body_id))
                hotspots.extend(ring.signals.to_sqlalchemy_hotspot_dicts(ring_id))
    upsert_all(partitioner.session, HotspotsDB, hotspots, ["ring_id", "commodity_sym"], ["id"])


type MetadataDB = Union[CommoditiesDB, ShipsDB, ShipModulesDB]


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
    Layer 5: (TODO)
      - MarketCommoditiesDB
      - ShipyardShipsDB
      - OutfittingShipModulesDB
      - HotspotsDB

    """

    def __init__(self) -> None:
        self.session = SessionLocal()
        self.id_cache: Dict[int, int] = {}

    def cache_spansh_entity_id(self, entity: BaseSpanshModel, db_id: int) -> None:
        self.cache_spansh_entity_id_by_key(entity.to_cache_key(), db_id)

    def cache_spansh_entity_id_by_key(self, key: int, db_id: int) -> None:
        if db_id is None:
            raise ValueError(f"Cannot cache None id for key: {key}")
        self.id_cache[key] = db_id
        logger.debug(f"CACHED Spansh Key: '{db_id}' - '{key}'")

    def get_spansh_entity_id(self, entity: BaseSpanshModel) -> int:
        return self.get_spansh_entity_id_by_key(entity.to_cache_key())

    def get_spansh_entity_id_by_key(self, key: int) -> int:
        if key not in self.id_cache:
            raise KeyError(f"Key not cached: {key}")
        return self.id_cache[key]

    metadata_cache: Dict[str, MetadataDB] = {}

    def cache_metadata_by_name(self, data: MetadataDB, name: str) -> None:
        if not name:
            raise ValueError(f"Cannot cache Falsey id for metadata: {data}")
        self.metadata_cache[name] = data

    def get_metadata_by_name(self, name: str) -> MetadataDB:
        if name not in self.metadata_cache:
            raise KeyError(f"Metadata not cached: {name}")
        return self.metadata_cache[name]

    commodity_names_by_category: Dict[str, set[str]] = {}

    def store_commodity_name_by_category(self, commodity_name: str, category: str) -> None:
        if category not in self.commodity_names_by_category:
            self.commodity_names_by_category[category] = set()
        self.commodity_names_by_category[category].add(commodity_name)

    def get_commodity_names_by_category(self, category: str) -> set[str]:
        return self.commodity_names_by_category[category]

    def _upsert_and_cache[T: BaseModelWithId](
        self,
        model_cls: Type[T],
        spansh_entities: Iterable[BaseSpanshModel],
        to_dict_fn: Callable[[BaseSpanshModel], dict[str, Any]],
        pk_keys: list[str],
    ) -> None:
        rows = [to_dict_fn(entity) for entity in spansh_entities]
        db_objs = upsert_all(self.session, model_cls, rows, pk_keys, ["id"])

        by_key = {e.to_cache_key(): e for e in spansh_entities}
        for db_obj in db_objs:
            spansh_entity = by_key.get(db_obj.to_cache_key())
            if spansh_entity is None:
                raise Exception(f"Missing Spansh entity for DB object: {pformat(db_obj)}")
            self.cache_spansh_entity_id(spansh_entity, db_obj.id)

    def load_metadata_yaml_into_pg(self, path: Path) -> None:
        logger.debug(f"Inserting '{path}'")

        with open(path, "r") as f:
            dict = yaml.load(f.read(), Loader=yaml.Loader)
            commodities = []
            for sym, values in dict.items():
                name = values.get("name")
                if name is None:
                    raise ValueError("Got a commodity with a None name!")
                category = values.get("category")
                if category is None:
                    raise ValueError("Got a commodity with a None category!")

                self.store_commodity_name_by_category(name, category)

                commodities.append(
                    {
                        "symbol": sym,
                        "name": name,
                        "avg_price": values.get("avg_price"),
                        "rare_goods": values.get("rare_goods"),
                        "corrosive": values.get("corrosive"),
                        "category": category,
                        "is_mineable": values.get("is_mineable"),
                        "ring_types": values.get("ring_types"),
                        "mining_method": values.get("mining_method"),
                        "has_hotspots": values.get("has_hotspots", False),
                    }
                )

            commodity_objects = upsert_all(self.session, CommoditiesDB, commodities, ["symbol"], [])
            logger.debug(pformat(commodity_objects))
            for commodity in commodity_objects:
                self.cache_metadata_by_name(commodity, commodity.name)

        logger.info(f"Imported {path.name} successfully")

    def insert_systems(self, input_systems: List[SystemSpansh]) -> None:
        insert_layer1(self, input_systems)
        insert_layer2(self, input_systems)
        insert_layer3(self, input_systems)
        insert_layer4(self, input_systems)
        insert_layer5(self, input_systems)


class SpanshDataPipeline:
    def __init__(self) -> None:
        self.session = SessionLocal()
        self.partitioner = SpanshDataLayerPartitioner()
        self.pipeline_timer = Timer("Spansh data import pipeline")

    @staticmethod
    def download_data() -> None:
        GALAXY_POPULATED_JSON_GZ.parent.mkdir(parents=True, exist_ok=True)

        download_file(GALAXY_POPULATED_JSON_URL, GALAXY_POPULATED_JSON_GZ)
        ungzip(GALAXY_POPULATED_JSON_GZ, GALAXY_POPULATED_JSON)

    def load_and_process_data(self, batch_process_fn: Callable[[List[SystemSpansh]], None]) -> None:
        start_at = 0
        skipping_past_every = 1000

        validated_every = 500  # 250#500
        process_every = 1500  # 500#1500
        processed_count = 0

        with GALAXY_POPULATED_JSON.open("r") as f:
            parser = ijson.items(f, "item")
            batch: List[SystemSpansh] = []

            skip_timer = Timer("Skipping rows to known min index")
            validate_timer = Timer("Pydantic validation timer")
            for idx, system_dict in enumerate(parser, start=1):
                if idx < start_at:
                    if idx % skipping_past_every == 0:
                        time_elapsed = seconds_to_str(skip_timer.lap(False))
                        running_for = self.pipeline_timer.running_for_str()
                        logger.info(f"Skipping past {idx} (Took {time_elapsed})(Total Running: {running_for})")
                    continue

                processed_count += 1
                try:
                    model = SystemSpansh.model_validate(system_dict)
                    batch.append(model)
                except Exception as e:
                    logger.warning(f"Validation failed at item {idx}: {e}")
                    continue

                if idx % validated_every == 0:
                    time_elapsed = seconds_to_str(skip_timer.lap(False))
                    running_for = self.pipeline_timer.running_for_str()
                    logger.info(
                        f"Validated {validated_every} systems in {time_elapsed} "
                        f"({idx} total)(Total Running: {running_for})"
                    )

                if idx % process_every == 0:
                    batch_process_fn(batch)
                    batch.clear()
                    import gc

                    gc.collect()
                    validate_timer.reset()

            if batch:
                batch_process_fn(batch)
                batch.clear()
                gc.collect()

        logger.info(f">> {processed_count} Systems")
        self.pipeline_timer.end()

        return None

    def process_data_batch(self, system_batch: List[SystemSpansh]) -> None:
        process_timer = Timer(f"Spansh datadump batch process {len(system_batch)}")

        self.partitioner.insert_systems(system_batch)

        upsert_time = process_timer.running_for_str()
        pipeline_time = self.pipeline_timer.running_for_str()
        logger.info(
            (
                f"Upserted {len(system_batch)} systems into postgres "
                f"(Took {upsert_time})(Total Running: {pipeline_time})"
            )
        )

    def run(self) -> None:
        for path in METADATA_DIR.rglob(COMMODITIES_YAML_FMT):
            self.partitioner.load_metadata_yaml_into_pg(path)

        self.load_and_process_data(self.process_data_batch)


log_level = logging.DEBUG


def main() -> None:
    configure_logger(log_level)

    pipeline = SpanshDataPipeline()
    pipeline.run()


def download_spansh() -> None:
    configure_logger(log_level)

    SpanshDataPipeline.download_data()


if __name__ == "__main__":
    main()
