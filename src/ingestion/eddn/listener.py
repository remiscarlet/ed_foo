#!python
import importlib
import json
import traceback
import zlib
from pprint import pformat
from types import ModuleType
from typing import Any, Callable, cast

import zmq
from gen.eddn_models import (
    approachsettlement_v1_0,
    commodity_v3_0,
    fsssignaldiscovered_v1_0,
    journal_v1_0,
)
from pydantic import BaseModel

from src.common.logging import get_logger
from src.ingestion.eddn.schemas import get_schema_model_mapping
from src.postgresql import SessionLocal
from src.postgresql.adapter import FactionsAdapter, StationsAdapter, SystemsAdapter
from src.postgresql.db import FactionPresencesDB, MarketCommoditiesDB, SystemsDB
from src.postgresql.utils import upsert_all

logger = get_logger(__name__)

module_mapping: dict[str, ModuleType] = {}


def import_generated_models() -> None:
    for schema, model_file in get_schema_model_mapping().items():
        module_path = f"gen.eddn_models.{model_file}"
        module = importlib.import_module(module_path)
        logger.debug(module.Model)  # Ensure model is valid and importable
        module_mapping[schema] = module


def get_module_from_schema(schema: str) -> ModuleType:
    module = module_mapping.get(schema)
    if module is None:
        raise RuntimeError(f"Tried getting a module for a schema we didn't know about! '{schema}'")
    return module


class EDDNListener:
    # TODO: Consider dependency ordering of inserts for new system/stations
    # Eg, if we're seeing market commodities for a system we don't have in the DB, there should be a pending
    # upsert for the station/system that needs to go through before we can upsert the market commodities themselves,
    # which have a FK on the stations table, ie station needs to be upserted first.
    processor_mapping: dict[type[BaseModel], Callable[[Any], None]]

    def __init__(self) -> None:
        self.session = SessionLocal()

        self.processor_mapping = {
            commodity_v3_0.Model: self.process_commodity_v3_0,
            # approachsettlement_v1_0.Model: self.process_approachsettlement_v1_0,
            journal_v1_0.Model: self.process_journal_v1_0,
            # fsssignaldiscovered_v1_0.Model: self.process_fsssignaldiscovered_v1_0,
        }

    def process_commodity_v3_0(self, model: commodity_v3_0.Model) -> None:
        """
        Process commodity-v3.0 EDDN messages
        """
        # May want to filter any stations with "invalid characters" like '$' or ';'
        # Some station names come through like '$EXT_PANEL_ColonisationShip; Skvortsov Territory'
        station_name = model.message.stationName

        try:
            station = StationsAdapter().get_station(station_name)
        except ValueError:
            logger.warning(f"Encountered station name that we don't know about! '{station_name}'")
            return

        commodity_dicts = MarketCommoditiesDB.to_dicts_from_eddn(model, station.id)
        upsert_all(self.session, MarketCommoditiesDB, commodity_dicts)

        logger.info(
            "[Market Commodities Updated] "
            f"{model.message.systemName} - {station_name} - {len(model.message.commodities)} Commodities"
        )

    @staticmethod
    def approachsettlement_v1_0_model_to_controlling_faction_id(model: approachsettlement_v1_0.Model) -> int | None:
        faction_id = None
        controlling_faction = getattr(model.message, "SystemFaction", None)
        if controlling_faction is not None:
            faction_name = controlling_faction.get("Name")
            faction = FactionsAdapter().get_faction(faction_name)
            if faction is not None:
                faction_id = faction.id

        return faction_id

    def process_approachsettlement_v1_0(self, model: approachsettlement_v1_0.Model) -> None:
        pass
        # controlling_faction_id = EDDNListener.approachsettlement_v1_0_model_to_controlling_faction_id(model)
        # system_dict = SystemsDB.to_dict_from_eddn(model, controlling_faction_id)
        # logger.info(pformat(system_dict))

    @staticmethod
    def journal_v1_0_model_to_faction_name_to_id_mapping(model: journal_v1_0.Model) -> dict[str, int]:
        mapping: dict[str, int] = {}
        for faction in model.message.Factions or []:
            faction_name = faction.Name
            if faction_name is None:
                logger.warning(f"Encountered Faction object with no Name! '{pformat(faction)}'")
                continue
            faction_obj = FactionsAdapter().get_faction(faction_name)
            if faction_obj is not None:
                mapping[faction_name] = faction_obj.id

        return mapping

    def process_journal_v1_0(self, model: journal_v1_0.Model) -> None:
        """
        Process journal-v1.0 EDDN messages
        """
        # if model.message.Factions is not None:
        system_name = cast(str, model.message.StarSystem)
        try:
            system = SystemsAdapter().get_system(system_name)
        except ValueError:
            # We currently only track systems with population > 0, so plenty of systems won't be found.
            logger.debug(f"Encountered system we didn't know about! '{system_name}'")
            return

        faction_id_mapping = EDDNListener.journal_v1_0_model_to_faction_name_to_id_mapping(model)
        faction_name_mapping = {v: k for k, v in faction_id_mapping.items()}

        controlling_faction_name = getattr(model.message, "SystemFaction", {}).get("Name")
        controlling_faction_id = (
            faction_id_mapping.get(cast(str, controlling_faction_name))
            if controlling_faction_name is not None
            else None
        )

        system_dict = SystemsDB.to_dict_from_eddn(model, controlling_faction_id)
        upsert_all(self.session, SystemsDB, [system_dict])
        logger.info(f"[System Updated] {system_name}")

        faction_presence_dicts = FactionPresencesDB.to_dicts_from_eddn(model, system.id, faction_id_mapping)
        try:
            upsert_all(self.session, FactionPresencesDB, faction_presence_dicts)
        except Exception:
            logger.warning(traceback.format_exc())
            logger.warning(pformat(faction_presence_dicts))
            logger.warning(pformat(model.message.Factions))
            return

        for faction in faction_presence_dicts or []:
            faction_id = faction.get("faction_id") or -1
            faction_name = faction_name_mapping.get(faction_id)
            logger.info(f"[Faction Presence Updated] {system_name} - {faction_name} - {faction.get("state")}")

    def process_fsssignaldiscovered_v1_0(self, model: fsssignaldiscovered_v1_0.Model) -> None:
        for signal in model.message.signals:
            if signal.SignalType in ["FleetCarrier", "Combat", "ResourceExtraction"]:
                continue
            if signal.SpawningPower is None:
                continue
            logger.info(pformat(signal))
            # logger.info(pformat([
            #     signal.SignalType, signal.SignalName, signal.SpawningPower, signal.SpawningState
            # ]))

    def run(self) -> None:
        ctx = zmq.Context()
        sub = ctx.socket(zmq.SUB)
        sub.connect("tcp://eddn.edcd.io:9500")

        sub.setsockopt_string(zmq.SUBSCRIBE, "")

        import_generated_models()

        print("Listening for messages...")
        while True:
            msg = sub.recv_multipart()
            d = json.loads(zlib.decompress(msg[0]))
            schema = d.get("$schemaRef")
            if schema is None:
                logger.warning("Could not find a valid $schema field in decoded EDDN message!")
                logger.warning(pformat(d))
                continue

            module = get_module_from_schema(schema)
            try:
                obj = module.Model.model_validate(d)
            except Exception:
                logger.error(traceback.format_exc())
                logger.info(pformat(d))
                continue

            obj_type = type(obj)
            if issubclass(obj_type, BaseModel) and obj_type in self.processor_mapping:
                try:
                    self.processor_mapping[obj_type](obj)
                except Exception:
                    logger.error(traceback.format_exc())


def main() -> None:
    listener = EDDNListener()
    listener.run()


if __name__ == "__main__":
    main()
