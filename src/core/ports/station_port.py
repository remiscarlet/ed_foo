from abc import ABC, abstractmethod

from src.core.models.station_model import Station


class StationPort(ABC):
    @abstractmethod
    def upsert_station(self, station: Station) -> Station:
        pass

    @abstractmethod
    def get_station(self, station_name: str) -> Station:
        pass

    @abstractmethod
    def delete_station(self, station_name: str) -> None:
        pass
