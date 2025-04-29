from abc import ABC, abstractmethod
from typing import Dict

from src.core.models.system_model import System


class DataDumpRetrievalPort(ABC):
    @abstractmethod
    def download_data(self) -> None:
        pass

    @abstractmethod
    def load_data(self) -> Dict[str, System]:
        pass
