#!python

import argparse
import textwrap
import traceback
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pprint import pformat
from typing import Dict, List, NamedTuple

from src.argparse_actions import StoreSystemNameWithCoords
from src.logging import configure_logger, get_logger
from src.populated_galaxy_systems import PopulatedGalaxySystems
from src.timer import Timer
from src.types.commodities import CommodityCategory, MineableSymbols
from src.utils import TopNStack, get_time_since
from tabulate import tabulate  # type: ignore

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    argparser = argparse.ArgumentParser(
        __name__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
    Calculates the best mineable commodity to mine in the supplied system.

    Calculated by:
    - Gather best sell prices at stations in-system for mineables
    - Compare against available hotspots in-system
    - Return best combination.
      - Can return no combinations. Eg, no ringed bodies in the system.
    """
        ),
    )
    argparser.add_argument(
        "--category",
        dest="category_filters",
        action="append",
        help="Category of commodity to search",
        default=None,
    )
    argparser.add_argument(
        "-n",
        "--number",
        action="store",
        type=int,
        help="Number of top commodity prices to list",
        default=25,
    )
    argparser.add_argument(
        "-s",
        "--system",
        action=StoreSystemNameWithCoords,
        type=str,
        help="Current system name. If we don't know about this system, will default to Sol",
        default="Sol",
    )
    argparser.add_argument(
        "-max",
        "--max-market-data-age",
        action="store",
        type=int,
        help="Max age of data before it's disregarded",
        default=3,
    )
    argparser.add_argument(
        "-M",
        "--min-supply-demand",
        action="store",
        type=int,
        help="Only includes commodities with at least this much Supply or Demand, whichever is relevant per --buy.",
        default=200,
    )
    argparser.add_argument(
        "-R",
        "--routes",
        action="store",
        type=int,
        help="Number of routes to display",
        default=5,
    )
    argparser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0)

    args = argparser.parse_args()
    if args.category_filters is None:
        args.category_filters = [
            CommodityCategory.MINERALS,
            CommodityCategory.METALS,
            # CommodityCategory.CHEMICALS, # Tritium
        ]
    return args


class PotentialMiningRoute(NamedTuple):
    mineable_symbol: MineableSymbols
    ring_name: str
    station_name: str
    sell_price: int
    demand: int
    update_time: datetime
    time_since_update: str


class MiningRoute(NamedTuple):
    mineable_symbol: MineableSymbols
    ring_name: str
    station_name: str
    price: int
    demand: int
    time_since_update: str


def route_scoring_fn(mining_route: PotentialMiningRoute) -> int:
    dataAge = datetime.now(timezone.utc) - mining_route.update_time
    if dataAge <= timedelta(days=2):
        decay = 1.0
    elif dataAge <= timedelta(days=4):
        decay = 0.75
    elif dataAge <= timedelta(days=7):
        decay = 0.5
    else:
        decay = 0.25

    price_weight = 0.98
    demand_weight = 1 - price_weight
    score = int((mining_route.demand**demand_weight) * (mining_route.sell_price**price_weight) * decay)
    route = [mining_route.mineable_symbol.value, mining_route.sell_price, mining_route.demand]

    logger.debug(f"ROUTE SCORE({score}) - {pformat(route)}")

    return score


def run(args: argparse.Namespace) -> None:
    system = PopulatedGalaxySystems.get_system(args.system)
    if system is None:
        raise Exception(f"Did not know about the system '{args.system}'!")

    logger.info("")
    logger.info("====== SYSTEM ======")
    logger.info(f"Name: {system.name}")
    logger.info("")

    # Get commodity prices
    return_buy_prices = False
    station_name = None
    prices = system.get_top_commodity_prices_per_station(
        top_n=args.number,
        return_buy_prices=return_buy_prices,
        min_supply_demand=args.min_supply_demand,
        station_name=station_name,
        category_filter=args.category_filters,
        max_data_age_days=args.max_market_data_age,
    )
    if not prices:
        logger.info("!! Found NO stations with known markets!")

    # Get hotspot info
    num_commodities = sum([len(top_n.to_list()) for top_n in prices.values()])
    logger.info(f"Got {len(prices)} stations with {num_commodities} total commodities")
    for station_name, top_n_stack in prices.items():
        for commodity in top_n_stack.to_list():
            logger.debug(f"{station_name} - {commodity.symbol} - {commodity.demand}x {commodity.sellPrice}CR")

    hotspots = system.get_hotspot_rings()
    if not hotspots:
        logger.info("!! Found NO hotspots in this system!")

    # Pre-process hotspots
    num_uniq_mineables = len(set([mineable.symbol for signals in hotspots.values() for mineable in signals.keys()]))
    num_hotspots = sum([count for hotspot in hotspots.values() for count in hotspot.values()])
    logger.info(f"Got {len(hotspots)} rings with {num_uniq_mineables} unique mineables across {num_hotspots} hotspots")

    hotspot_commodities = {mineable.symbol for hotspot in hotspots.values() for mineable in hotspot.keys()}

    logger.debug("")
    logger.debug("?? HOTSPOT COMMODITIES")
    logger.debug(pformat(hotspot_commodities))

    ringnames_by_commodity: Dict[MineableSymbols, List[str]] = defaultdict(lambda: [])
    for ring_name, hotspot in hotspots.items():
        for mineable in hotspot.keys():
            sym = MineableSymbols(mineable.symbol)
            ringnames_by_commodity[sym].append(ring_name)

    logger.debug("")
    logger.debug("?? RINGNAMES BY COMMODITY")
    logger.debug(ringnames_by_commodity)

    # Get Top N Mining Routes
    potential_routes = TopNStack[PotentialMiningRoute](args.routes, route_scoring_fn)
    for station_name, commodities in prices.items():
        for commodity in commodities.to_list():
            if commodity.symbol not in hotspot_commodities:
                continue
            time_since_update = get_time_since(commodity.updateTime) if commodity.updateTime is not None else "Unknown"
            try:
                sym = MineableSymbols(commodity.name)
                potential_routes.insert(
                    PotentialMiningRoute(
                        sym,
                        ring_name,
                        station_name,
                        commodity.sellPrice,
                        commodity.demand,
                        commodity.updateTime or datetime.fromtimestamp(0),
                        time_since_update,
                    )
                )
            except ValueError:
                logger.trace(traceback.format_exc())

    for potential_route in potential_routes.to_list():
        logger.debug("")
        logger.debug("?? POTENTIAL ROUTE")
        logger.debug(pformat(potential_route))

    table: List[MiningRoute] = []
    for potential_route in potential_routes.to_list():

        [mineable_symbol, ring_name, station_name, sell_price, demand, _update_time, time_since_update] = (
            potential_route
        )

        logger.debug("")
        logger.debug("??  MINEABLE SYMBOL AND HOTSPOT COMMODITIES")
        logger.debug(pformat([mineable_symbol, ringnames_by_commodity.keys()]))
        for ring_name in ringnames_by_commodity.get(mineable_symbol, []):
            table.append(MiningRoute(mineable_symbol, ring_name, station_name, sell_price, demand, time_since_update))

    headers = ["Commodity", "Ring Name", "Station", "Price", "Demand", "Updated Last"]
    logger.info(tabulate(table, headers))
    logger.info("")

    logger.info(
        "Note: Market data relies on EDDN/Spansh dumps. "
        "Not all stations may have market data uploaded and prices may be stale."
    )


if __name__ == "__main__":
    with Timer("Script", True):
        args = parse_args()
        configure_logger(args)
        run(args)
