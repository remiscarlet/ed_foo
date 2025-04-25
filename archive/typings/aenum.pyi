from enum import Enum
from typing import Any, Callable, Type, TypeVar

class StrEnum(Enum):  # type: ignore[misc]
    ...

def enum(*, value: str, **metadata: Any) -> Enum: ...
def member(*, value: str, **metadata: Any) -> Callable[[Any], Any]: ...

_TEnum = TypeVar("_TEnum", bound=Enum)

def extend_enum(
    enum_class: Type[_TEnum],
    name: str,
    value: Any,
    **kwargs: Any,
) -> _TEnum: ...
