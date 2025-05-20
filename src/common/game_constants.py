from pathlib import Path

import yaml
from gen.metadata_models.commodities_schema import Commodity as CommodityModel
from gen.metadata_models.commodities_schema import Model as CommoditiesByNameModel

from src.common.constants import COMMODITIES_YAML_FMT, METADATA_DIR
from src.common.logging import get_logger

logger = get_logger(__name__)

commodities_mapping: dict[str, CommodityModel] = {}
identifier_to_symbol_mapping: dict[str, str] = {}


def get_metadata_by_capi_name(capi_name: str) -> CommodityModel | None:
    if not commodities_mapping:
        load_metadata()
    return commodities_mapping.get(capi_name)


def get_symbol_by_capi_name(capi_name: str) -> str | None:
    if not identifier_to_symbol_mapping:
        load_metadata()
    return identifier_to_symbol_mapping.get(capi_name)


def load_metadata() -> None:
    for path in METADATA_DIR.rglob(COMMODITIES_YAML_FMT):
        load_metadata_file(path)


def load_metadata_file(path: Path) -> None:
    logger.debug(f"Inserting '{path}'")

    with open(path, "r") as f:
        dict = yaml.load(f.read(), Loader=yaml.Loader)
        commodities = CommoditiesByNameModel.model_validate(dict)

        for sym, commodity in commodities.root.items():
            assert type(sym) is str

            lookup_names: list[str] = [
                sym,  # Eg, "LowTemperatureDiamond" # EDDI Keynames - Corresponds to CommoditiesDB pks (symbol)
                sym.lower(),  # Eg, "lowtemperaturediamond" # Used as commodity names in EDDN (CAPI) Commodity models
                commodity.name,  # Eg, "Low Temperature Diamond" # Human readable
            ]

            for insert_name in lookup_names:
                commodities_mapping[insert_name] = commodity
                identifier_to_symbol_mapping[insert_name] = sym
