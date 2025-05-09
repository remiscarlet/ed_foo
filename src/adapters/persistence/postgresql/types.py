from datetime import datetime
from typing import Any

from pydantic import BaseModel


# From: sql/functions/get_hotspots_in_system_v1.sql
# From: sql/functions/get_hotspots_in_system_by_commodities_v1.sql
class HotspotResult(BaseModel):
    system_name: str
    body_name: str
    ring_name: str
    ring_type: str
    commodity: str
    count: int


# From: sql/functions/get_top_commodities_in_system_v1.sql
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


class SystemResult(BaseModel):
    name: str
    x: float
    y: float
    z: float
    allegiance: str
    population: int
    primary_economy: str
    secondary_economy: str
    security: str
    government: str
    body_count: int
    controlling_power: str
    power_conflict_progress: list[dict[str, float]]
    power_state: str
    power_state_control_progress: float
    power_state_reinforcement: float
    power_state_undermining: float
    powers: list[str]
    thargoid_war: dict[str, Any] | None
