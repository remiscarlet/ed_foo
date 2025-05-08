from datetime import datetime
from typing import Optional

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
    updated_at: Optional[datetime]
    rank: int
