from pathlib import Path
from pprint import pformat

import yaml
from gen.metadata_models.commodities_schema import Commodity as CommodityModel
from gen.metadata_models.commodities_schema import Model as CommoditiesByNameModel
from gen.metadata_models.strings_schema import Model as StringMappingModel

from ekaine.common.constants import COMMODITIES_YAML_FMT, METADATA_DIR, STRINGS_YAML_FMT
from ekaine.common.logging import get_logger

logger = get_logger(__name__)

commodities_mapping: dict[str, CommodityModel] = {}
identifier_to_symbol_mapping: dict[str, str] = {}


def get_metadata_by_eddn_name(eddn_name: str) -> CommodityModel | None:
    if not commodities_mapping:
        load_metadata()
    return commodities_mapping.get(eddn_name)


def get_symbol_by_eddn_name(eddn_name: str) -> str | None:
    if not identifier_to_symbol_mapping:
        load_metadata()
    return identifier_to_symbol_mapping.get(eddn_name)


def load_metadata() -> None:
    for path in METADATA_DIR.rglob(COMMODITIES_YAML_FMT):
        load_commodity_metadata_file(path)
    for path in METADATA_DIR.rglob(STRINGS_YAML_FMT):
        load_string_metadata_file(path)


def add_identifier_to_symbol_mapping(val: str, sym: str) -> None:
    identifier_to_symbol_mapping[val] = sym

    has_prefix = val[0] == "$"
    has_suffix = val[-1] == ";"
    if not has_prefix or not has_suffix:
        wrapped_val = "" if has_prefix else "$"
        wrapped_val += val
        wrapped_val += "" if has_suffix else ";"
        identifier_to_symbol_mapping[wrapped_val] = sym


def load_string_metadata_file(path: Path) -> None:
    logger.debug(f"Loading '{path}'")

    with path.open("r") as f:
        data = yaml.load(f, Loader=yaml.Loader)

    strings = StringMappingModel.model_validate(data)

    for sym, mapped_val in strings.root.items():
        add_identifier_to_symbol_mapping(sym, sym)
        if isinstance(mapped_val, str):
            add_identifier_to_symbol_mapping(mapped_val, sym)
        elif isinstance(mapped_val, list):
            for val in mapped_val:
                add_identifier_to_symbol_mapping(val, sym)
        else:
            logger.warning("Got unknown type for string val! %s", pformat(mapped_val))


def load_commodity_metadata_file(path: Path) -> None:
    logger.debug(f"Loading '{path}'")

    with path.open("r") as f:
        data = yaml.load(f, Loader=yaml.Loader)

    commodities = CommoditiesByNameModel.model_validate(data)

    for sym, commodity in commodities.root.items():
        assert type(sym) is str

        lookup_names: list[str] = [
            sym,  # Eg, "LowTemperatureDiamond" # EDDI Keynames - Corresponds to CommoditiesDB pks (symbol)
            sym.lower(),  # Eg, "lowtemperaturediamond" # Used as commodity names in EDDN (CAPI) Commodity models
            commodity.name,  # Eg, "Low Temperature Diamond" # Human readable
        ]

        for insert_name in lookup_names:
            commodities_mapping[insert_name] = commodity
            add_identifier_to_symbol_mapping(insert_name, sym)
