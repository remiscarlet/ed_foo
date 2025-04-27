from sqlalchemy import (
    ARRAY,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    relationship,
)
from sqlalchemy.dialects.postgresql import JSONB

from src.adapters.persistence.postgresql import BaseModel


class CommodityPriceDTO(DataClassJsonMixin):
    buyPrice: int
    demand: int
    sellPrice: int
    supply: int
    updateTime: Optional[datetime] = None


class CommodityDTO(CommodityPriceDTO):
    category: str  # src.core.models.commodity.CommodityCategory
    commodityId: int
    name: str
    symbol: str


class MarketDTO(DataClassJsonMixin):
    commodities: Optional[List[CommodityDTO]] = None
    prohibitedCommodities: Optional[List[str]] = None
    updateTime: Optional[datetime] = None


class ShipModuleDTO(DataClassJsonMixin):
    category: str
    cls: int = field(metadata=config(field_name="class"))
    moduleId: int
    name: str
    rating: str
    symbol: str

    ship: Optional[str] = None


class OutfittingDTO(DataClassJsonMixin):
    modules: List[ShipModuleDTO]
    updateTime: datetime


class ShipDTO(DataClassJsonMixin):
    name: str
    shipId: int
    symbol: str


class ShipyardDTO(DataClassJsonMixin):
    ships: List[ShipDTO]
    updateTime: datetime


class StationDTO(BaseModel):
    __tablename__ = "station"

    id64 = Column(Integer, primary_key=True, index=True)
    id = Column(Integer, index=True)
    name = Column(String, index=True)
    updateTime = Column(DateTime)

    system_id = Column(Integer, ForeignKey("systems.id"), nullable=False)
    system = relationship("SystemDB", back_populates="stations")

    allegiance = Column(String)
    controllingFaction = Column(String)
    controllingFactionState = Column(String)
    distanceToArrival = Column(Float)
    economies = Column(JSONB)

    primaryEconomy = Column(String)
    government = Column(String)

    # landingPads
    smallLandingPad = Column(Integer)
    mediumLandingPad = Column(Integer)
    largeLandingPad = Column(Integer)

    market: Optional[MarketDTO] = None
    outfitting: Optional[OutfittingDTO] = None
    shipyard: Optional[ShipyardDTO] = None

    services = Column(ARRAY(String))
    type = Column(String)

    carrierName = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
