from abc import ABC, abstractmethod
from typing import Self


class ToCoreModel[T](ABC):
    @abstractmethod
    def to_core_model(self) -> T:
        pass


class FromCoreModel[T](ABC):
    @classmethod
    @abstractmethod
    def to_core_model(cls: type[Self], t: T) -> Self:
        pass
