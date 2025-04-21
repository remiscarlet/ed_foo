from datetime import datetime
from typing import Any, Dict

import dataclasses_json

from .commodities import *  # noqa: F401, F403
from .common import *  # noqa: F401, F403
from .station import *  # noqa: F401, F403
from .system import *  # noqa: F401, F403

dataclasses_json.cfg.global_config.encoders[datetime] = datetime.isoformat
dataclasses_json.cfg.global_config.decoders[datetime] = datetime.fromisoformat


def _default_serialize(o: Any) -> Dict[str, Any]:
    if hasattr(o, "to_dict"):
        return o.to_dict()  # type: ignore
    raise TypeError(f"Type {o!r} not serializable")
