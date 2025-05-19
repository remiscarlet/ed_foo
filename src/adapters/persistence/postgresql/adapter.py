from typing import Sequence

from sqlalchemy import RowMapping, select, text

from src.adapters.persistence.postgresql import SessionLocal
from src.adapters.persistence.postgresql.db import SystemsDB
from src.adapters.persistence.postgresql.types import (
    HotspotResult,
    MiningAcquisitionResult,
    MiningReinforcementResult,
    SystemResult,
    TopCommodityResult,
)
from src.common.logging import get_logger
from src.common.timer import Timer
from src.common.utils import dur_to_interval_str
from src.core.models.system_model import System
from src.core.ports.api_command_port import ApiCommandPort
from src.core.ports.system_port import SystemPort

logger = get_logger(__name__)


class ApiCommandAdapter(ApiCommandPort):
    def __init__(self) -> None:
        self.session = SessionLocal()

    def get_acquirable_systems_from_origin(self, system_name: str) -> list[SystemResult]:
        stmt = text("SELECT * FROM api.get_acquirable_systems_from_origin(:system_name)")

        result = self.session.execute(stmt, {"system_name": system_name})

        rows: Sequence[RowMapping] = result.mappings().all()
        return [SystemResult(**row) for row in rows]

    def get_expandable_systems_in_range(self, system_name: str) -> list[SystemResult]:
        stmt = text("SELECT * FROM api.get_expandable_systems_in_range(:system_name)")

        result = self.session.execute(stmt, {"system_name": system_name})

        rows: Sequence[RowMapping] = result.mappings().all()
        return [SystemResult(**row) for row in rows]

    def get_hotspots_in_system(self, system_name: str) -> list[HotspotResult]:
        stmt = text("SELECT * FROM api.get_hotspots_in_system(:system_name)")

        result = self.session.execute(stmt, {"system_name": system_name})

        rows: Sequence[RowMapping] = result.mappings().all()
        return [HotspotResult(**row) for row in rows]

    def get_hotspots_in_system_by_commodities(
        self, system_name: str, commodities_filter: list[str]
    ) -> list[HotspotResult]:
        stmt = text(
            """SELECT * FROM api.get_hotspots_in_system_by_commodities(
                :system_name, :commodities_filter)"""
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

    def get_mining_expandable_systems_in_range(self, system_name: str) -> list[MiningAcquisitionResult]:
        stmt = text("SELECT * FROM api.get_mining_expandable_systems_in_range(:system_name)")

        result = self.session.execute(stmt, {"system_name": system_name})

        rows: Sequence[RowMapping] = result.mappings().all()
        return [MiningAcquisitionResult(**row) for row in rows]

    def get_top_reinforcement_mining_routes(
        self,
        power_name: str,
        power_states: list[str] | None = None,
        commodity_names: list[str] | None = None,
        ignored_ring_types: list[str] | None = None,
        min_sell_price: int = 50000,
        min_demand: int = 10,
        num_results: int = 25,
        max_data_age_dur_str: str = "3d",
    ) -> list[MiningReinforcementResult]:
        power_states = power_states or ["Exploited", "Fortified"]
        commodity_names = commodity_names or ["Monazite", "Platinum"]
        ignored_ring_types = ignored_ring_types or ["Metal Rich"]

        stmt = text(
            """
            SELECT *
            FROM api.get_top_reinforcement_mining_routes(
                :power_name, :power_states, :commodity_names, :ignored_ring_types,
                :min_sell_price, :min_demand, :num_results, :max_data_age_interval
            )
        """
        )

        max_data_age_interval = dur_to_interval_str(max_data_age_dur_str)

        result = self.session.execute(
            stmt,
            {
                "power_name": power_name,
                "power_states": power_states,
                "commodity_names": commodity_names,
                "ignored_ring_types": ignored_ring_types,
                "min_sell_price": min_sell_price,
                "min_demand": min_demand,
                "num_results": num_results,
                "max_data_age_interval": max_data_age_interval,
            },
        )

        rows: Sequence[RowMapping] = result.mappings().all()
        return [MiningReinforcementResult(**row) for row in rows]

    def get_systems_with_power(self, power_name: str, power_states: list[str] | None = None) -> list[SystemResult]:
        params: dict[str, str | list[str]] = {"power_name": power_name}
        if power_states:
            params["power_states"] = power_states
            stmt = text("SELECT * FROM api.get_systems_with_power(:power_name, :power_states)")
        else:
            stmt = text("SELECT * FROM api.get_systems_with_power(:power_name)")

        result = self.session.execute(stmt, params)

        rows: Sequence[RowMapping] = result.mappings().all()
        return [SystemResult(**row) for row in rows]

    def get_top_commodities_in_system(
        self, system_name: str, comms_per_station: int, min_supplydemand: int, is_buying: bool
    ) -> list[TopCommodityResult]:
        stmt = text(
            """SELECT * FROM api.get_top_commodities_in_system(
                :system_name, :comms_per_station, :min_supplydemand, :is_buying)"""
        )

        result = self.session.execute(
            stmt,
            {
                "system_name": system_name,
                "comms_per_station": comms_per_station,
                "min_supplydemand": min_supplydemand,
                "is_buying": is_buying,
            },
        )

        rows: Sequence[RowMapping] = result.mappings().all()
        return [TopCommodityResult(**row) for row in rows]


class SystemsAdapter(SystemPort):
    def __init__(self) -> None:
        self.session = SessionLocal()

    def upsert_systems(self, systems: list[System]) -> None:
        pass

    def get_system(self, system_name: str) -> System:
        query = select(SystemsDB).where(SystemsDB.name == system_name)
        db_system = self.session.scalars(query).first()
        logger.info(db_system)
        if not db_system:
            raise ValueError("System not found")
        return db_system.to_core_model()

    def delete_system(self, system_name: str) -> None:
        pass
