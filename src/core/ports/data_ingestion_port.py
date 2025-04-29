from abc import ABC, abstractmethod
from typing import Dict

from src.core.models.system_model import System


class DataIngestionPort(ABC):
    @abstractmethod
    def get_systems(self) -> Dict[str, System]:
        pass
