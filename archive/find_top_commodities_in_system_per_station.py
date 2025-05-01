#!python

import argparse
import textwrap

from tabulate import tabulate  # type: ignore

from src.argparse_actions import StoreSystemNameWithCoords
from src.logging import configure_logger, get_logger
from src.populated_galaxy_systems import PopulatedGalaxySystems
from src.timer import Timer
from src.utils import get_time_since

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    argparser = argparse.ArgumentParser(
        __name__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
    Prints top N commodities at each station in system
    """
        ),
    )
    # TODO: Category-based search?
    # argparser.add_argument(
    #     "--category",
    #     dest="category",
    #     action="store",
    #     type=str,
    #     help="Category of commodity to search",
    #     default=None,
    # )
    argparser.add_argument(
        "-s",
        "--system",
        action=StoreSystemNameWithCoords,
        type=str,
        help="Current system name. If we don't know about this system, will default to Sol",
        default="Sol",
    )
    argparser.add_argument(
        "-S",
        "--station",
        action="store",
        type=str,
        help="If provided, only returns prices for this station, assuming it exists in the target system",
        default=None,
    )
    argparser.add_argument(
        "-n",
        "--number",
        action="store",
        type=int,
        help="Number of top commodity prices to list",
        default=5,
    )
    argparser.add_argument(
        "-b",
        "--buy",
        action="store_true",
        help="If supplied, calculates based on BUY price. Defaults to SELL price.",
        default=False,
    )
    argparser.add_argument(
        "-M",
        "--min-supply-demand",
        action="store",
        type=int,
        help="Only includes commodities with at least this much Supply or Demand, whichever is relevant per --buy.",
        default=1,
    )
    argparser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0)

    return argparser.parse_args()


def run(args: argparse.Namespace) -> None:
    system = PopulatedGalaxySystems.get_system(args.system)
    if system is None:
        raise Exception(f"Did not know about the system '{args.system}'!")

    prices = system.get_top_commodity_prices_per_station(
        args.number, args.buy, args.min_supply_demand, args.station, None, 3
    )

    logger.info("")
    logger.info("====== SYSTEM ======")
    logger.info(f"Name: {system.name}")
    logger.info("")
    if not prices:
        logger.info("!! Found NO stations with known markets!")

    for system_name, commodities in prices.items():
        headers = ["Station Name", "Commodity", "Sell Price", "Demand", "Buy Price", "Supply", "Updated Last"]
        table = []
        for commodity in commodities.to_list():

            time_since_update = get_time_since(commodity.updateTime) if commodity.updateTime is not None else "Unknown"
            table.append(
                [
                    system_name,
                    commodity.name,
                    commodity.sellPrice,
                    commodity.demand,
                    commodity.buyPrice,
                    commodity.supply,
                    time_since_update,
                ]
            )
        logger.info(tabulate(table, headers))
        logger.info("")

    logger.info(
        "Note: Market data relies on EDDN/Spansh dumps. "
        "Not all stations may have market data uploaded and prices may be stale."
    )


if __name__ == "__main__":
    with Timer("Script"):
        args = parse_args()
        configure_logger(args)
        run(args)
