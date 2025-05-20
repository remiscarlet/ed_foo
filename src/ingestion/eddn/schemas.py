import importlib
import json
import logging
from pathlib import Path
from pprint import pprint
from typing import Any, cast

from src.common.constants import EDDN_SCHEMA_MAPPING_FILE, EDDN_SCHEMAS_DIR
from src.common.logging import configure_logger, get_logger

logger = get_logger(__name__)


def get_schema_model_mapping() -> dict[str, Any]:
    with open(EDDN_SCHEMA_MAPPING_FILE, "r") as f:
        d = json.load(f)
    return cast(dict[str, Any], d)


def filename_to_model_file(file: Path) -> str:
    return file.stem.replace("-", "_").replace(".", "_")


def generate_mapping() -> None:
    configure_logger(logging.INFO)
    logger.info(">> Generating EDDN Model Mapping JSON")
    logger.info("")
    mapping: dict[str, str] = {}

    for file in EDDN_SCHEMAS_DIR.iterdir():
        if file.suffix != ".json":
            continue
        model_file = filename_to_model_file(file)

        with open(file, "r") as f:
            data = json.load(f)
            schema = data.get("id")
            if schema is None:
                raise RuntimeError(f"Schema file '{file}' didn't seem to have a valid 'id' field!")
            schema = schema.replace("#", "")  # Remove fragment identifier ('#') if exists

        module_path = f"gen.eddn_models.{model_file}"
        module = importlib.import_module(module_path)

        pprint([file, module.Model])  # Ensure model is valid and importable

        mapping[schema] = model_file

    with open(EDDN_SCHEMA_MAPPING_FILE, "w") as f:
        json.dump(mapping, f)
