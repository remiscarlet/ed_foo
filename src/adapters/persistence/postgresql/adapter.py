from typing import List, Sequence

from sqlalchemy import RowMapping, select, text

from src.adapters.persistence.postgresql import SessionLocal
from src.adapters.persistence.postgresql.db import SystemsDB
from src.adapters.persistence.postgresql.types import HotspotResult, TopCommodityResult
from src.common.timer import Timer
from src.core.models.system_model import System
from src.core.ports.api_command_port import ApiCommandPort
from src.core.ports.system_port import SystemPort


class ApiCommandAdapter(ApiCommandPort):
    def __init__(self) -> None:
        self.session = SessionLocal()

    def get_hotspots_in_system(self, system_name: str) -> List[HotspotResult]:
        stmt = text(
            """
            SELECT * FROM api.get_hotspots_in_system(
                :system_name
            )
        """
        )

        result = self.session.execute(
            stmt,
            {
                "system_name": system_name,
            },
        )

        rows: Sequence[RowMapping] = result.mappings().all()
        return [HotspotResult(**row) for row in rows]

    def get_hotspots_in_system_by_commodities(
        self, system_name: str, commodities_filter: List[str]
    ) -> List[HotspotResult]:
        stmt = text(
            """
            SELECT * FROM api.get_hotspots_in_system_by_commodities(
                :system_name,
                :commodities_filter
            )
        """
        )

        timer = Timer("get_hotspots_in_system_by_commodities")
        result = self.session.execute(
            stmt,
            {
                "system_name": system_name,
                "commodities_filter": commodities_filter,
            },
        )

        rows: Sequence[RowMapping] = result.mappings().all()
        rtn = [HotspotResult(**row) for row in rows]

        timer.end()
        return rtn

    def get_top_commodities_in_system(
        self, system_name: str, comms_per_station: int, min_supplydemand: int, is_selling: bool
    ) -> List[TopCommodityResult]:
        stmt = text(
            """
            SELECT * FROM api.get_top_commodities_in_system(
                :system_name,
                :comms_per_station,
                :min_supplydemand,
                :is_selling
            )
        """
        )

        result = self.session.execute(
            stmt,
            {
                "system_name": system_name,
                "comms_per_station": comms_per_station,
                "min_supplydemand": min_supplydemand,
                "is_selling": is_selling,
            },
        )

        rows: Sequence[RowMapping] = result.mappings().all()
        return [TopCommodityResult(**row) for row in rows]


class SystemsAdapter(SystemPort):
    def __init__(self) -> None:
        self.session = SessionLocal()

    def upsert_systems(self, systems: List[System]) -> None:
        pass

    def get_system(self, system_name: str) -> System:
        query = select(SystemsDB).where(SystemsDB.name.is_(system_name))
        db_system = self.session.scalars(query).first()
        if not db_system:
            raise Exception("System not found")
        return db_system.to_core_model()

    def delete_system(self, system_name: str) -> None:
        pass
