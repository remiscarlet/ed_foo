import traceback
from datetime import datetime, timezone
from typing import Any, Dict, Protocol

from marshmallow import Schema


class HasSchema(Protocol):
    @classmethod
    def schema(cls) -> Schema: ...


def get_time_since(dt: datetime) -> str:
    """Returns a string of weeks, days, hours since supplied `dt`
    Eg, timedelta(days=20, hours=5) => "2 Weeks, 6 Days, 5 Hours Ago"
        timedelta(days=1, hours=1) => "1 Week, 1 Hour Ago"
    """
    delta = datetime.now(timezone.utc) - dt

    days = delta.days
    seconds = delta.total_seconds() - (days * 24 * 60 * 60)
    hours = seconds // (60 * 60)
    config = {
        "Week": int(days // 7),
        "Day": int(days % 7),
        "Hour": int(hours),
    }

    parts = []
    for unit, num in config.items():
        if num > 0:
            part = f"{num} {unit}"
            if num > 1:
                part += "s"
            parts.append(part)

    time_since = ", ".join(parts)
    return f"{time_since} Ago"


def debug_dataclasses_json_load(schema_type: type[HasSchema], data: Dict[str, Any]) -> None:
    schema = schema_type.schema()
    for name, field in schema.fields.items():
        try:
            print(f"Decoding field {name!r}: {type(data[name])}")
            # this will invoke only the logic for that one field
            field.deserialize(data[name], name, data)
        except Exception:
            print(f"Error decoding field {name!r}:")
            traceback.print_exc()
            break
