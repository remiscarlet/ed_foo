import json
from pathlib import Path

import jsonschema
import yaml
from jsonschema import Draft202012Validator, RefResolver

from ekaine.common.constants import (
    COMMODITIES_SCHEMA,
    COMMODITIES_YAML_FMT,
    ENUMS_SCHEMA,
    METADATA_DIR,
    STRINGS_SCHEMA,
    STRINGS_YAML_FMT,
)


def main() -> None:
    validate_schemas(COMMODITIES_SCHEMA, COMMODITIES_YAML_FMT, [ENUMS_SCHEMA])
    validate_schemas(STRINGS_SCHEMA, STRINGS_YAML_FMT)


def validate_schemas(schema_path: Path, yaml_file_glob_fmt: str, ref_schema_paths: list[Path] | None = None) -> None:
    # Commodities Schema Check
    with open(schema_path, "r") as f:
        schema = json.load(f)

    schema_store = {}
    for ref_schema_path in ref_schema_paths or []:
        with open(ref_schema_path) as f:
            ref_schema = json.load(f)
            schema_store[ref_schema_path.name] = ref_schema

    validator = Draft202012Validator(schema=schema, resolver=RefResolver.from_schema(schema, store=schema_store))
    failed = []
    for yml_file in METADATA_DIR.rglob(yaml_file_glob_fmt):
        with open(yml_file, "r") as f:
            data = yaml.safe_load(f)

        try:
            validator.validate(data)
            print(f"Validated '{yml_file.name}' successful!")
        except jsonschema.exceptions.ValidationError as e:
            print(f"FAILED to validate '{yml_file.name}'!")
            print(e.message)
            failed.append(yml_file.name)

    if failed:
        raise RuntimeError("Failed to validate all yaml files!")


if __name__ == "__main__":
    main()
