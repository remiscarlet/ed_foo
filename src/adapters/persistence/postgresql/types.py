from datetime import datetime
from typing import Any

from pydantic import BaseModel


# From: sql/functions/api_get_hotspots_in_system_v1.sql
# From: sql/functions/api_get_hotspots_in_system_by_commodities_v1.sql
class HotspotResult(BaseModel):
    system_name: str
    body_name: str
    ring_name: str
    ring_type: str
    commodity: str
    count: int


# From: sql/functions/api_get_top_commodities_in_system_v1.sql
class TopCommodityResult(BaseModel):
    system_name: str
    station_name: str
    station_type: str
    distance_to_arrival: float
    commodity: str
    sell_price: int
    demand: int
    buy_price: int
    supply: int
    updated_at: datetime | None
    rank: int


# From: sql/functions/api_get_acquirable_systems_from_origin_v1.sql
# From: sql/functions/api_get_expandable_systems_in_range_v1.sql
# From: sql/functions/api_get_systems_with_power_v1.sql
class SystemResult(BaseModel):
    name: str
    x: float
    y: float
    z: float
    allegiance: str | None
    population: int
    primary_economy: str | None
    secondary_economy: str | None
    security: str | None
    government: str | None
    body_count: int
    controlling_power: str | None
    power_conflict_progress: list[dict[str, Any]] | None
    power_state: str | None
    power_state_control_progress: float | None
    power_state_reinforcement: float | None
    power_state_undermining: float | None
    powers: list[str] | None
    thargoid_war: dict[str, Any] | None

    @property
    def power_conflict_progress_str(self) -> str:
        if self.power_conflict_progress is None:
            return "No Conflict"

        self.power_conflict_progress.sort(key=lambda d: d.get("power", ""))

        power_strs = []
        for power in self.power_conflict_progress:
            power_strs.append(f"{power.get('power')}: {power.get('progress')}")

        return ", ".join(power_strs)


# From: sql/functions/api_get_mining_expandable_systems_in_range.sql
class MiningAcquisitionResult(BaseModel):
    expanding_system: str
    ring_name: str
    commodity: str
    unoccupied_system: str
    station_name: str
    sell_price: int
    demand: int
