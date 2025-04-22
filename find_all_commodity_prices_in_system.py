#!python

import argparse
import textwrap

from tabulate import tabulate  # type: ignore

from src.argparse_actions import StoreSystemNameWithCoords
from src.logging import configure_logger, get_logger
from src.populated_galaxy_systems import PopulatedGalaxySystems
from src.timer import Timer
from src.types import CommodityType
from src.utils import get_time_since

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    argparser = argparse.ArgumentParser(
        __name__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
    Prints all known prices for supplied commodities in the target system.
    """
        ),
    )
    argparser.add_argument(
        "--commodity",
        dest="commodities",
        action="append",
        type=str,
        help="Commodity to print prices for in system",
        choices=list(CommodityType),
        default=None,
    )
    argparser.add_argument(
        "--system",
        action=StoreSystemNameWithCoords,
        type=str,
        help="Current system name. If we don't know about this system, will default to Sol",
        default="Sol",
    )
    argparser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0)

    args = argparser.parse_args()
    if args.commodities is None:
        args.commodities = [CommodityType.PLATINUM, CommodityType.MONAZITE]  # type: ignore

    return args


def run(args: argparse.Namespace) -> None:
    system = PopulatedGalaxySystems.get_system(args.system)
    if system is None:
        raise Exception(f"Did not know about the system '{args.system}'!")

    prices = system.get_commodities_prices(args.commodities)

    logger.info("")
    logger.info("====== SYSTEM ======")
    logger.info(f"Name: {system.name}")
    logger.info(f"Target Commodities: {[comm.value for comm in args.commodities]}")
    logger.info("")
    if not prices:
        logger.info("!! Found NO stations with known markets for the target commodities!")

    headers = ["System Name", "Commodity", "Sell Price", "Demand", "Buy Price", "Supply", "Updated Last"]
    table = []
    for system_name, commodities in prices.items():
        for commodity_name, price in commodities.items():
            time_since_update = get_time_since(price.updateTime) if price.updateTime is not None else "Unknown"
            table.append(
                [
                    system_name,
                    commodity_name,
                    price.sellPrice,
                    price.demand,
                    price.buyPrice,
                    price.supply,
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
    args = parse_args()
    configure_logger(args)

    with Timer("Script", True):
        run(args)
