import traceback
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Protocol

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


class TopNStack[T]:
    def __init__(self, n: int, scoring_fn: Callable[[T], int]) -> None:
        """Creates a DS to keep track of the top N instances of T using key as the value function.

        Stack should be sorted high to low in the list (Eg, [10, 5, 1])
        """
        self.stack: List[T] = []
        self.n = n
        self.scoring_fn = scoring_fn

    def __repr__(self) -> str:
        return f"TopNStack({len(self.stack)})"

    def to_list(self) -> List[T]:
        return self.stack

    def insert(self, to_insert: T) -> None:
        """Inserts `to_insert` into the stack and pops the "lowest" item if stack exceeds size `self.n`"""
        insert_idx = 0
        if self.is_empty():
            self.stack.insert(insert_idx, to_insert)

        found = False
        for idx, item in enumerate(self.stack):
            if self.scoring_fn(to_insert) > self.scoring_fn(item):
                insert_idx = idx
                found = True
                break

        if found:
            self.stack.insert(insert_idx, to_insert)

        if self.size() > self.n:
            self.stack.pop(-1)

    def pop(self) -> Optional[T]:
        if self.is_empty():
            return None
        return self.stack.pop(0)

    def is_empty(self) -> bool:
        return len(self.stack) == 0

    def size(self) -> int:
        return len(self.stack)
