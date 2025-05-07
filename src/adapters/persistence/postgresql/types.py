from pydantic import BaseModel


class HotspotResult(BaseModel):
    system_name: str
    body_name: str
    ring_name: str
    ring_type: str
    commodity: str
    count: int
