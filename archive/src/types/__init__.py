import types
from datetime import datetime
from pprint import pformat
from typing import Any, Dict, Union, get_args, get_origin

import dataclasses_json
import dataclasses_json.core as _core
from src.logging import get_logger

dataclasses_json.cfg.global_config.encoders[datetime] = datetime.isoformat
dataclasses_json.cfg.global_config.decoders[datetime] = datetime.fromisoformat

logger = get_logger(__name__)

_original_decode = _core._decode_generic


def _decode_generic(type_: Any, value: Any, infer_missing: bool) -> Any:
    """Custom decoder for dataclasses_json

    dataclasses_json can't handle `Optional[datetime]` because at runtime,
    the field value is either None or datetime, not `Optional[datetime]`.
    As such if the target type was an Optional,unwrap that Optional and
    just use the inner type for the purposes of decoding.
    """

    # if it’s an Optional[T] or PEP 604 T|None
    origin = get_origin(type_)
    if origin in (Union, types.UnionType):
        args = get_args(type_)
        # detect Optional (T, NoneType)
        if len(args) == 2 and args[1] is type(None):
            inner = args[0]
            # if they registered a decoder for inner, and we got a str
            if inner in dataclasses_json.cfg.global_config.decoders and isinstance(value, str):
                logger.trace(
                    pformat([inner, value[:100], infer_missing, dataclasses_json.cfg.global_config.decoders[inner]])
                )
                return dataclasses_json.cfg.global_config.decoders[inner](value)
    # fall back to the normal path
    try:
        logger.trace(pformat([type_, value[:100], infer_missing]))
    except Exception:
        pass
    return _original_decode(type_, value, infer_missing)  # type: ignore


_core._decode_generic = _decode_generic


def _default_serialize(o: Any) -> Dict[str, Any]:
    if hasattr(o, "to_dict"):
        return o.to_dict()  # type: ignore
    raise TypeError(f"Type {o!r} not serializable")


__all__ = []

from .commodities import (  # noqa: F401, E402
    Chemicals,
    CommodityType,
    HasMineableMetadata,
    Metals,
    MineableMetadata,
    Mineables,
    MineableSymbols,
    Minerals,
    MiningMethod,
    RingType,
)
from .common import (  # noqa: F401, E402
    Coordinates,
    Timestamps,
)
from .station import (  # noqa: F401, E402
    Commodity,
    CommodityPrice,
    Market,
    Outfitting,
    Ship,
    ShipModule,
    Shipyard,
    Station,
)
from .system import (  # noqa: F401, E402
    AcquisitionSystemPairings,
    Asteroids,
    Body,
    ControllingFaction,
    PlayerMinorFaction,
    PowerplaySystem,
    Signals,
    System,
)

__all__.extend(
    [
        # Commodities
        "MiningMethod",
        "RingType",
        "MineableMetadata",
        "HasMineableMetadata",
        "Chemicals",
        "Minerals",
        "Metals",
        "Mineables",
        "MineableSymbols",
        "CommodityType",
        # Common
        "Coordinates",
        "Timestamps",
        # Station
        "CommodityPrice",
        "Commodity",
        "Market",
        "ShipModule",
        "Outfitting",
        "Ship",
        "Shipyard",
        "Station",
        # System
        "PlayerMinorFaction",
        "ControllingFaction",
        "Signals",
        "Asteroids",
        "Body",
        "System",
        "PowerplaySystem",
        "AcquisitionSystemPairings",
    ]
)
