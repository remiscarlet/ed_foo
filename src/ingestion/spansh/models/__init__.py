from datetime import datetime
from typing import Any, Callable, Tuple, Type

from pydantic import BaseModel, ConfigDict, field_validator


def parse_flexible_datetime(v: str) -> datetime:
    if isinstance(v, datetime):
        return v

    if isinstance(v, str):
        try:
            return datetime.fromisoformat(v)
        except ValueError:
            print(v)

        # Timestamps can come with a "+00" suffix which is technically not iso compliant
        if v.endswith("+00"):
            v += "00"
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S%z")
        except ValueError:
            pass
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
        raise ValueError(f"Invalid datetime format: {v}")

    raise TypeError(f"Cannot parse {type(v)} into datetime")


class BaseSpanshModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=lambda s: "".join(word.capitalize() if i > 0 else word for i, word in enumerate(s.split("_"))),
        populate_by_name=True,
        extra="allow",
        frozen=True,
    )

    def to_cache_key(self, *args: Any, **kwargs: Any) -> int:
        return hash(self.to_cache_key_tuple(*args, **kwargs))

    def to_cache_key_tuple(self, *args: Any, **kwargs: Any) -> Tuple[Any, ...]:
        raise NotImplementedError()

    @classmethod
    def flexible_datetime_validator(cls: Type[Any], field_name: str) -> Callable[[str], datetime]:
        @field_validator(field_name, mode="before")
        def _validate(v: str) -> datetime:
            return parse_flexible_datetime(v)

        return _validate
