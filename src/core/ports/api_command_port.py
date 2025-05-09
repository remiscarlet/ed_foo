from abc import ABC, abstractmethod

from src.adapters.persistence.postgresql.types import HotspotResult, TopCommodityResult


class ApiCommandPort(ABC):
    @abstractmethod
    def get_hotspots_in_system(self, system_name: str) -> list[HotspotResult]:
        pass

    @abstractmethod
    def get_hotspots_in_system_by_commodities(
        self, system_name: str, commodities_filter: list[str]
    ) -> list[HotspotResult]:
        pass

    @abstractmethod
    def get_top_commodities_in_system(
        self, system_name: str, comms_per_station: int, min_supplydemand: int, is_buying: bool
    ) -> list[TopCommodityResult]:
        pass
