import json

import jsonschema
import yaml
from jsonschema import Draft202012Validator, RefResolver

from src.common.constants import (
    COMMODITIES_SCHEMA,
    COMMODITIES_YAML_FMT,
    ENUMS_SCHEMA,
    METADATA_DIR,
)


def main():
    # Commodities Schema Check
    with open(COMMODITIES_SCHEMA, "r") as schema_file:
        commodities_schema = json.load(schema_file)

    with open(ENUMS_SCHEMA) as f:
        enums_schema = json.load(f)

    schema_store = {
        "enums.schema.json": enums_schema,
    }

    validator = Draft202012Validator(
        schema=commodities_schema, resolver=RefResolver.from_schema(commodities_schema, store=schema_store)
    )
    for commodity_yaml in METADATA_DIR.rglob(COMMODITIES_YAML_FMT):
        with open(commodity_yaml, "r") as yaml_file:
            data = yaml.safe_load(yaml_file)

        try:
            validator.validate(data)
            print(f"Validated '{commodity_yaml.name}' successful!")
        except jsonschema.exceptions.ValidationError as e:
            print(f"Validating '{commodity_yaml.name}' failed!")
            print(e.message)


if __name__ == "__main__":
    main()
