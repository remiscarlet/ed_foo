import asyncio
import logging  # noqa: F401
from datetime import datetime, timedelta, timezone
from pathlib import Path
from pprint import pformat
from typing import Any, Callable, Iterable, Type

import aiofiles  # noqa: F401
import ijson
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
from src.common.logging import get_logger
from src.common.timer import Timer
from src.common.utils import download_file, seconds_to_str, ungzip
from src.ingestion.spansh.models import BaseSpanshModel
from src.ingestion.spansh.models.body_spansh import AsteroidsSpansh, BodySpansh
from src.ingestion.spansh.models.station_spansh import StationSpansh
from src.ingestion.spansh.models.system_spansh import (
    ControllingFactionSpansh,
    FactionSpansh,
    SystemSpansh,
)

logger = get_logger(__name__)


def upsert_all[T: BaseModel](
    session: Session,
    model: Type[T],
    rows: list[dict[str, Any]],
    conflict_cols: list[str],
    exclude_update_cols: list[str] = [],
    debug_print_extra_cols: list[str] = [],
) -> list[T]:
    if not rows:
        return []

    cols_to_print = conflict_cols + debug_print_extra_cols
    logger.debug(f"{len(rows)} {model.__name__} items being upserted...")
    logger.trace(repr([{k: v for k, v in item.items() if k in cols_to_print} for item in rows]))

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

    results = session.scalars(stmt.returning(model), execution_options={"populate_existing": True})
    session.commit()

    return list(iter(results.all()))


def insert_layer1(partitioner: "SpanshDataLayerPartitioner", input_systems: list[SystemSpansh]) -> None:
    logger.info(f"Layer 1: Factions ({partitioner.total_running_str_fn()})")

    all_factions: dict[str, FactionSpansh | ControllingFactionSpansh] = {}
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


def insert_layer2(partitioner: "SpanshDataLayerPartitioner", input_systems: list[SystemSpansh]) -> None:
    logger.info(f"Layer 2: Systems ({partitioner.total_running_str_fn()})")

    systems = []
    system_by_key: dict[int, SystemSpansh] = {}

    for system in input_systems:
        system_by_key[system.to_cache_key()] = system
        controlling_id = (
            partitioner.get_spansh_entity_id(system.controlling_faction) if system.controlling_faction else None
        )
        systems.append(system.to_sqlalchemy_dict(controlling_faction_id=controlling_id))

    system_objects = upsert_all(partitioner.session, SystemsDB, systems, ["name"], ["id"])

    for system_obj in system_objects:
        spansh_system = system_by_key.get(system_obj.to_cache_key())
        if spansh_system is None:
            raise Exception(f"Spansh system not found for DB system '{system_obj.to_cache_key_tuple()}'")
        partitioner.cache_spansh_entity_id(spansh_system, system_obj.id)


def insert_layer3(partitioner: "SpanshDataLayerPartitioner", input_systems: list[SystemSpansh]) -> None:
    logger.info(f"Layer 3: FactionPresences and Bodies ({partitioner.total_running_str_fn()})")

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


def insert_layer4(partitioner: "SpanshDataLayerPartitioner", input_systems: list[SystemSpansh]) -> None:
    logger.info(f"Layer 4: Stations, Signals, Rings ({partitioner.total_running_str_fn()})")

    # --- Stations ---
    rows_by_key: dict[int, dict[str, Any]] = {}
    stations_by_key: dict[int, StationSpansh] = {}

    for system in input_systems:
        system_id = partitioner.get_spansh_entity_id(system)

        for station in system.stations or []:
            cache_key = station.to_cache_key(system_id)
            row = station.to_sqlalchemy_dict(system_id, "system")

            rows_by_key[cache_key] = row
            stations_by_key[cache_key] = station

        for body in system.bodies or []:
            body_id = partitioner.get_spansh_entity_id(body)

            for station in body.stations or []:
                cache_key = station.to_cache_key(body_id)
                row = station.to_sqlalchemy_dict(body_id, "body")

                rows_by_key[cache_key] = row
                stations_by_key[cache_key] = station

    station_objects = upsert_all(
        partitioner.session, StationsDB, list(rows_by_key.values()), ["name", "owner_id"], ["id"]
    )

    for station_obj in station_objects:
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
    rings_by_key: dict[int, AsteroidsSpansh] = {}
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


def insert_layer5(partitioner: "SpanshDataLayerPartitioner", input_systems: list[SystemSpansh]) -> None:
    logger.info(f"Layer 4: Market, Outfitting, Shipyard, Hotspots ({partitioner.total_running_str_fn()})")

    # --- Market ---

    commodities: list[dict[str, Any]] = []

    now = datetime.now(timezone.utc)
    max_data_age = timedelta(days=partitioner.max_market_data_age_days)

    def extract_commodities(owner_id: int, station: StationSpansh) -> None:
        if station.market is None:
            return
        elif station.market.update_time is not None:
            data_age = now - station.market.update_time
            if data_age > max_data_age:
                return

        logger.trace(pformat(station.to_cache_key_tuple(owner_id)))
        station_id = partitioner.get_spansh_entity_id_by_key(station.to_cache_key(owner_id))

        for commodity in station.market.commodities or []:
            commodities.append(commodity.to_sqlalchemy_dict(station_id, commodity.symbol))

    for system in input_systems:
        for station in system.stations or []:
            system_id = partitioner.get_spansh_entity_id(system)
            extract_commodities(system_id, station)
        for body in system.bodies or []:
            body_id = partitioner.get_spansh_entity_id(body)
            for station in body.stations:
                extract_commodities(body_id, station)

    upsert_all(
        partitioner.session,
        MarketCommoditiesDB,
        commodities,
        ["station_id", "commodity_sym"],
        ["id"],
    )

    # --- Outfitting ---

    modules: list[dict[str, Any]] = []

    def extract_modules(owner_id: int, station: StationSpansh) -> None:
        if station.outfitting is None:
            return
        station_id = partitioner.get_spansh_entity_id_by_key(station.to_cache_key(owner_id))  # noqa: F841
        # TODO: Import module metadata first
        # for module in station.outfitting.modules:
        #     module_id = partitioner.get_metadata_by_name(module.symbol)
        #     modules.append(module.to_sqlalchemy_dict(station_id, module_id))

    for system in input_systems:
        system_id = partitioner.get_spansh_entity_id(system)
        for station in system.stations or []:
            extract_modules(system_id, station)
        for body in system.bodies or []:
            body_id = partitioner.get_spansh_entity_id(body)
            for station in body.stations:
                extract_modules(body_id, station)

    upsert_all(partitioner.session, OutfittingShipModulesDB, modules, ["station_id", "module_id"], ["id"])

    # --- Shipyard ---
    ships: list[dict[str, Any]] = []

    def extract_ships(owner_id: int, station: StationSpansh) -> None:
        if station.outfitting is None:
            return
        station_id = partitioner.get_spansh_entity_id_by_key(station.to_cache_key(owner_id))  # noqa: F841
        # for ship in station.shipyard.ships:
        #     ship_id = partitioner.get_metadata_by_name(ship.symbol)
        #     ships.append(ship.to_sqlalchemy_dict(station_id, ship_id))

    for system in input_systems:
        system_id = partitioner.get_spansh_entity_id(system)
        for station in system.stations or []:
            extract_ships(system_id, station)
        for body in system.bodies or []:
            body_id = partitioner.get_spansh_entity_id(body)
            for station in body.stations:
                extract_ships(body_id, station)

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


type MetadataDB = CommoditiesDB | ShipsDB | ShipModulesDB


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

    def __init__(self, total_running_str_fn: Callable[[], str], max_market_data_age_days: int) -> None:
        self.session = SessionLocal()
        self.id_cache: dict[int, int] = {}
        self.total_running_str_fn = total_running_str_fn
        self.max_market_data_age_days = max_market_data_age_days

    def cache_spansh_entity_id(self, entity: BaseSpanshModel, db_id: int) -> None:
        self.cache_spansh_entity_id_by_key(entity.to_cache_key(), db_id, False)
        logger.trace(f"CACHED Spansh entity: '{db_id}' - '{repr(entity)}'")

    def cache_spansh_entity_id_by_key(self, key: int, db_id: int, log: bool = True) -> None:
        if db_id is None:
            raise ValueError(f"Cannot cache None id for key: {key}")

        self.id_cache[key] = db_id

        if log:
            logger.trace(f"CACHED Spansh Key: '{db_id}' - '{key}'")

    def get_spansh_entity_id(self, entity: BaseSpanshModel) -> int:
        return self.get_spansh_entity_id_by_key(entity.to_cache_key())

    def get_spansh_entity_id_by_key(self, key: int) -> int:
        if key not in self.id_cache:
            raise KeyError(f"Key not cached: {key}")
        return self.id_cache[key]

    metadata_cache: dict[str, MetadataDB] = {}

    def cache_metadata_by_name(self, data: MetadataDB, name: str) -> None:
        if not name:
            raise ValueError(f"Cannot cache Falsey id for metadata: {data}")
        self.metadata_cache[name] = data

    def get_metadata_by_name(self, name: str) -> MetadataDB:
        if name not in self.metadata_cache:
            raise KeyError(f"Metadata not cached: {name}")
        return self.metadata_cache[name]

    commodity_names_by_category: dict[str, set[str]] = {}

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

    def insert_systems(self, input_systems: list[SystemSpansh]) -> None:
        insert_layer1(self, input_systems)
        insert_layer2(self, input_systems)
        insert_layer3(self, input_systems)
        insert_layer4(self, input_systems)
        insert_layer5(self, input_systems)


class SpanshDataPipeline:
    def __init__(
        self,
        start_at_system_idx: int = 0,
        skipping_past_every: int = 1000,
        validated_every: int = 500,
        process_every: int = 1500,
        max_market_data_age_days: int = 30,
    ) -> None:
        self.start_at_system_idx = start_at_system_idx
        self.skipping_past_every = skipping_past_every
        self.validated_every = validated_every
        self.process_every = process_every
        self.max_market_data_age_days = max_market_data_age_days

        self.session = SessionLocal()
        self.pipeline_timer = Timer("Spansh data import pipeline")
        self.partitioner = SpanshDataLayerPartitioner(self.total_running_str, self.max_market_data_age_days)

    def total_running_str(self) -> str:
        return f"Total Running: {self.pipeline_timer.running_for_str()}"

    @staticmethod
    def download_data() -> None:
        GALAXY_POPULATED_JSON_GZ.parent.mkdir(parents=True, exist_ok=True)

        download_file(GALAXY_POPULATED_JSON_URL, GALAXY_POPULATED_JSON_GZ)
        ungzip(GALAXY_POPULATED_JSON_GZ, GALAXY_POPULATED_JSON)

    async def load_and_process_data(self, batch_process_fn: Callable[[list[SystemSpansh]], None]) -> None:
        processed_count = 0
        process_batch_lock = asyncio.Lock()
        idx_lock = asyncio.Lock()

        async with aiofiles.open(GALAXY_POPULATED_JSON, mode="r") as f:
            # with GALAXY_POPULATED_JSON.open("r") as f:
            skip_timer = Timer("Skipping rows to known min index")
            validate_timer = Timer("Pydantic validation timer")

            # parser = ijson.items(f, "item")
            # for idx, system_dict in enumerate(parser, start=1):
            batch: list[SystemSpansh] = []

            idx = 0
            async for system_dict in ijson.items(f, "item"):
                # for idx, system_dict in enumerate(ijson.items(f, "item"), start=1):
                async with idx_lock:
                    idx += 1

                if idx < self.start_at_system_idx:
                    if idx % self.skipping_past_every == 0:
                        time_elapsed = seconds_to_str(skip_timer.lap(False))
                        logger.info(f"Skipping past {idx} (Took {time_elapsed})({self.total_running_str()})")
                    continue

                processed_count += 1
                try:
                    model = SystemSpansh.model_validate(system_dict)
                    async with process_batch_lock:
                        batch.append(model)
                except Exception as e:
                    logger.warning(f"Validation failed at item {idx}: {e}")
                    continue

                if idx % self.validated_every == 0:
                    time_elapsed = seconds_to_str(skip_timer.lap(False))
                    logger.info(
                        f"Validated {self.validated_every} systems in {time_elapsed} "
                        f"({idx} total)({self.total_running_str()})"
                    )

                if idx % self.process_every == 0:
                    async with process_batch_lock:
                        old_batch = []
                        old_batch, batch = batch, old_batch

                    batch_process_fn(old_batch)

                    old_batch.clear()
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

    def process_data_batch(self, system_batch: list[SystemSpansh]) -> None:
        process_timer = Timer(f"Spansh datadump batch process {len(system_batch)}")

        self.partitioner.insert_systems(system_batch)

        upsert_time = process_timer.running_for_str()
        logger.info(
            (f"Upserted {len(system_batch)} systems into postgres " f"(Took {upsert_time})({self.total_running_str()})")
        )

    async def run(self) -> None:
        for path in METADATA_DIR.rglob(COMMODITIES_YAML_FMT):
            self.partitioner.load_metadata_yaml_into_pg(path)

        await self.load_and_process_data(self.process_data_batch)
