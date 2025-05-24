from gen.eddn_models import commodity_v3_0
from sqlalchemy.orm import Session

from ekaine.common.logging import get_logger
from ekaine.postgresql.adapter import StationsAdapter
from ekaine.postgresql.db import MarketCommoditiesDB
from ekaine.postgresql.utils import upsert_all

logger = get_logger(__name__)


def process_model(session: Session, model: commodity_v3_0.Model) -> None:
    """
    Process commodity-v3.0 EDDN messages

    Updates:
    - MarketCommoditiesDB

    """
    # May want to filter any stations with "invalid characters" like '$' or ';'
    # Some station names come through like '$EXT_PANEL_ColonisationShip; Skvortsov Territory'
    station_name = model.message.stationName

    try:
        station = StationsAdapter().get_station(station_name)
    except ValueError:
        logger.warning(f"Encountered station name that we don't know about! '{station_name}'")
        return

    commodity_dicts = MarketCommoditiesDB.to_dicts_from_eddn(model, station.id)
    upsert_all(session, MarketCommoditiesDB, commodity_dicts)

    logger.info(
        "[Market Commodities DB Updated] "
        f"{model.message.systemName} - {station_name} - {len(model.message.commodities)} Commodities"
    )
