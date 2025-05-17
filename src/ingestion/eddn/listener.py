#!python
import importlib
import json
import logging
import traceback
import typing
import zlib
from pprint import pformat, pprint
from types import ModuleType
from typing import Any

import zmq

from src.common.constants import EDDN_SCHEMA_MAPPING_FILE
from src.common.logging import configure_logger, get_logger

logger = get_logger(__name__)


def get_schema_model_mapping() -> dict[str, Any]:
    with open(EDDN_SCHEMA_MAPPING_FILE, "r") as f:
        d = json.load(f)
    return typing.cast(dict[str, Any], d)


module_mapping: dict[str, ModuleType] = {}


def import_generated_models() -> None:
    for schema, model_file in get_schema_model_mapping().items():
        module_path = f"gen.eddn_models.{model_file}"
        module = importlib.import_module(module_path)
        pprint(module.Model)  # Ensure model is valid and importable
        module_mapping[schema] = module


def get_module_from_schema(schema: str) -> ModuleType:
    module = module_mapping.get(schema)
    if module is None:
        raise RuntimeError(f"Tried getting a module for a schema we didn't know about! '{schema}'")
    return module


def eddn_listener() -> None:
    configure_logger(logging.INFO)

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
            pprint(obj)

        except Exception:
            traceback.print_exc()
