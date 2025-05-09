from abc import ABC, abstractmethod

from src.core.models.system_model import System


class SystemPort(ABC):
    @abstractmethod
    def upsert_systems(self, system: list[System]) -> None:
        pass

    @abstractmethod
    def get_system(self, system_name: str) -> System:
        pass

    @abstractmethod
    def delete_system(self, system_name: str) -> None:
        pass
