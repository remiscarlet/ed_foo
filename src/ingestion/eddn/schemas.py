import importlib
import json
from pathlib import Path
from pprint import pprint

from src.common.constants import EDDN_SCHEMA_MAPPING_FILE, EDDN_SCHEMAS_DIR


def filename_to_model_file(file: Path) -> str:
    return file.stem.replace("-", "_").replace(".", "_")


def generate_mapping() -> None:
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
            schema = schema[:-1]  # Truncate '#' suffix
        pprint([file, model_file, schema])

        module_path = f"gen.eddn_models.{model_file}"
        module = importlib.import_module(module_path)
        pprint(module.Model)  # Ensure model is valid and importable

        mapping[schema] = model_file

    with open(EDDN_SCHEMA_MAPPING_FILE, "w") as f:
        json.dump(mapping, f)
