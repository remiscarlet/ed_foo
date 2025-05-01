#!python

import argparse
import textwrap
from pprint import pformat
from typing import List

from src.argparse_actions import StoreMineableCommodities, StoreSystemNameWithCoords
from src.logging import configure_logger, get_logger
from src.populated_galaxy_systems import PopulatedGalaxySystems
from src.powerplay_systems import PowerplaySystems
from src.timer import Timer
from src.types import Coordinates, Mineables
from src.types.system import System
from src.utils import get_time_since

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    argparser = argparse.ArgumentParser(
        __name__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
    Hypothesis: There are reinforceable systems that have elevated commodity prices
                but we don't know about them because of data staleness.

    Faction state (Boom) information is revealed when entering a system, which is much more likely than exact
    commodity prices which requires a CMDR to dock at a specific station.

    As such, there exists a time delta between freshness of faction states and known commodity market prices.
    This script tries to analyze this delta for potential stations to check prices at for advantageous PP2.0 play

    Key points:
    - The fresher the faction state (Eg, Boom), the better
    - Market data staleness isn't strictly required, but the fresher
      the data the more likely it'll just show up on meritminer.cc normally.

    Finds reinforcement systems/stations that:
    - Has a minimum landing pad size of MIN_LANDING_PAD
    - Has a minimum population of MIN_POPULATION (Encourages higher commodity demand)
    - Has at least one TARGET MINERAL hotspot
    - Is in Boom
        - Has a market with data older than MIN_MARKET_DATA_AGE_IN_DAYS
        - Buys/Sells commodities in TARGET_COMMODITIES
    """
        ),
    )
    argparser.set_defaults(current_system="Sol", current_coords=Coordinates(0, 0, 0))
    argparser.add_argument(
        "-min", "--min-market-data-age", action="store", type=int, help="Minimum age of market data", default=3
    )
    argparser.add_argument(
        "-max",
        "--max-system-data-age",
        action="store",
        type=int,
        help="Maximum age of system/faction state data",
        default=2,
    )
    argparser.add_argument(
        "-ps",
        "--target-power-state",
        dest="target_power_states",
        action="append",
        choices=["Exploited", "Fortified", "Stronghold"],
        help="Power states to consider for reinforcement",
        default=["Exploited", "Fortified"],
    )
    argparser.add_argument(
        "-l",
        "--min-landing-pad-size",
        action="store",
        type=str,
        help="Minimum landing pad size",
        choices=["large", "medium", "small"],
        default="medium",
    )
    argparser.add_argument(
        "-c",
        "--target-commodity",
        dest="target_commodities",
        action=StoreMineableCommodities,
        type=Mineables,
        help="Mineable commodities to target",
        choices=list(Mineables),
    )
    argparser.add_argument("--max-distance", action="store", type=int, help="Max distance in LY to search", default=250)
    argparser.add_argument(
        "-p",
        "--min-population",
        action="store",
        type=int,
        help="Min population of target system. Higher population generally means higher commodity demand",
        default=100000,
    )
    argparser.add_argument(
        "-s",
        "--current-system",
        action=StoreSystemNameWithCoords,
        type=str,
        help="Current system name. If we don't know about this system, will default to Sol coords",
        default="Sol",
    )
    argparser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0)

    return argparser.parse_args()


def find_reinforceable_systems(args: argparse.Namespace) -> List[System]:
    # Exploited or Fortified systems in Boom under Nakato Kaine control
    with Timer("powerplay_systems.get_reinforcement_systems()"):
        boom_reinforcement_pp_systems = PowerplaySystems.get_reinforcement_systems(
            "Nakato Kaine",
            powerStates=args.target_power_states,
            factionStates=["Boom"],
            maxAgeInDays=args.max_system_data_age,
        )
    with Timer(f"db_hydration_timer - {len(boom_reinforcement_pp_systems)} systems"):
        boom_reinforcement_systems = PopulatedGalaxySystems.get_systems(
            list(map(lambda sys: sys.name, boom_reinforcement_pp_systems))
        )

    # Filter for unoccupied systems above minimum population and has at least one valid hotspot
    reinforceable_systems = [
        system
        for system in boom_reinforcement_systems
        if system.population > args.min_population and system.get_hotspot_rings(args.target_commodities)
    ]

    # Sort by distance
    reinforceable_systems.sort(
        reverse=True,
        key=lambda system: args.current_coords.distance_to(system.coords),
    )

    return reinforceable_systems


def run(args: argparse.Namespace) -> None:
    systems_count = 0
    stations_count = 0
    for system in find_reinforceable_systems(args):
        all_stations = system.get_stations_with_services(["Market"])

        stations = [
            station
            for station in all_stations
            if station.has_commodities(args.target_commodities, require_all=False)
            and station.has_minimum_landing_pad(args.min_landing_pad_size)
            and station.has_min_data_age_days(args.min_market_data_age)
        ]

        if stations:
            ring_hotspots = system.get_hotspot_rings(args.target_commodities)
            logger.info("")
            logger.info("")
            logger.info("===============================")
            logger.info("=        REINFORCEMENT?       =")
            logger.info("=========== SYSTEM ============")
            logger.info(f"Name: {system.name} ({system.powerState})")
            logger.info(f"Distance: {args.current_coords.distance_to(system.coords):.2f}LY")
            logger.info(f"Last Updated: {get_time_since(system.date)}")
            logger.info(f"Population: {system.population:,}")
            logger.info(f"Controlling Faction: {pformat(max(system.factions, key=lambda f: f.influence))}")
            for ring_name, hotspots in ring_hotspots.items():
                logger.info(f"++ {ring_name} ++")
                for mineral_type, hotspot_count in hotspots.items():
                    logger.info(f"  > {mineral_type}: {hotspot_count} Hotspots")

            logger.trace(pformat(system, depth=2))

        for station in stations:
            logger.info("")
            logger.info("== STATION")
            logger.info(f">> Name: {station.name} ({station.distanceToArrival:.2f}LS)")
            logger.info(f">> Last Updated: {get_time_since(station.updateTime)}")
            logger.info(f">> Economies: {station.economies}")
            logger.info(
                f">> Controlling Faction: {station.controllingFaction} (State: {station.controllingFactionState})"
            )
            for commodity in args.target_commodities:
                price = station.get_commodity_price(commodity)
                if price:
                    logger.info(f"!! {commodity} !! Last Known {pformat(price)}")

            logger.trace(pformat(station, depth=2))

        if stations:
            systems_count += 1
            stations_count += len(stations)

    logger.info("")
    logger.info("=============")
    logger.info(f"Systems: {systems_count}")
    logger.info(f"Stations: {stations_count}")


if __name__ == "__main__":
    with Timer("Script"):
        args = parse_args()
        configure_logger(args)
        run(args)
