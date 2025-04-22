#!python

import argparse
import textwrap
from pprint import pformat
from typing import Dict, List, Tuple

from src.argparse_actions import StoreMineableCommodities, StoreSystemNameWithCoords
from src.logging import configure_logger, get_logger
from src.populated_galaxy_systems import PopulatedGalaxySystems
from src.powerplay_systems import PowerplaySystems
from src.timer import Timer
from src.types import AcquisitionSystemPairings, Coordinates, Mineables, PowerplaySystem
from src.utils import get_time_since

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    argparser = argparse.ArgumentParser(
        __name__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
    Hypothesis: There are acquirable systems that have elevated commodity prices
                but we don't know about them because of data staleness.

    Faction state (Boom) information is revealed when entering a system, which is much more likely than exact
    commodity prices which requires a CMDR to dock at a specific station.

    As such, there exists a time delta between freshness of faction states and known commodity market prices.
    This script tries to analyze this delta for potential stations to check prices at for advantageous PP2.0 play

    Key points:
    - The fresher the faction state (Eg, Boom), the better
    - Market data staleness isn't strictly required, but the fresher the data
      the more likely it'll just show up on meritminer.cc normally.

    Finds acquisition systems/stations that:
    - Has a minimum landing pad size of MIN_LANDING_PAD
    - Has a minimum population of MIN_POPULATION (Encourages higher commodity demand)
    - Is in Boom
        - Has a market with data older than MIN_MARKET_DATA_AGE_IN_DAYS
        - Buys/Sells commodities in TARGET_COMMODITIES
    - In range of a reinforcement system
      - Reinforcement system has at least one TARGET MINERAL hotspot
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
        "-l",
        "--min-landing-pad-size",
        action="store",
        type=str,
        help="Minimum landing pad size",
        choices=["large", "medium", "small"],
        default="medium",
    )
    argparser.add_argument(
        "-m",
        "--mineables",
        dest="target_commodities",
        action=StoreMineableCommodities,
        type=Mineables,
        help="Mineable commodities to target",
        choices=list(Mineables),
    )
    argparser.add_argument(
        "-d", "--max-distance", action="store", type=int, help="Max distance in LY to search", default=250
    )
    argparser.add_argument(
        "-p",
        "--min-population",
        action="store",
        type=int,
        help="Min population of target acquisition system. Higher population generally means higher commodity demand",
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


def find_acquirable_systems(args: argparse.Namespace) -> List[AcquisitionSystemPairings]:
    # Unoccupied systems in Boom state under Nakato Kaine influence sphere
    with Timer("powerplay_systems.get_acquisition_systems()"):
        boom_nk_unoccupied_systems = PowerplaySystems.get_acquisition_systems(
            "Nakato Kaine",
            ["Boom"],
            args.max_system_data_age,
        )

    # Fortified or Stronghold systems under Nakato Kaine control
    with Timer("powerplay_systems.get_reinforcement_systems()"):
        nk_f_or_s_systems = PowerplaySystems.get_reinforcement_systems(
            "Nakato Kaine",
            ["Fortified", "Stronghold"],
            maxAgeInDays=30,
        )

    # Get all "acquisition pairs" to hydrate from the sqlite
    # We want to do it in one query to minimize query overhead
    acquisition_pairings: Dict[str, Tuple[PowerplaySystem, List[PowerplaySystem]]] = {}
    for target_sys in boom_nk_unoccupied_systems:
        for src_sys in nk_f_or_s_systems:
            if (
                src_sys.is_in_influence_range(target_sys)
                and args.current_coords.distance_to(target_sys.coords) <= args.max_distance
            ):
                if target_sys.name not in acquisition_pairings:
                    acquisition_pairings[target_sys.name] = (target_sys, [])
                acquisition_pairings[target_sys.name][1].append(src_sys)

    to_hydrate = set()
    for target_sys, acquisition_systems in acquisition_pairings.values():
        to_hydrate.add(target_sys.name)
        to_hydrate.update(map(lambda sys: sys.name, acquisition_systems))

    with Timer(f"db_hydration_timer - {len(to_hydrate)} systems"):
        PopulatedGalaxySystems.get_systems(list(to_hydrate))

    acquirable_systems: List[AcquisitionSystemPairings] = []
    for boom_unoccupied_pp_system, f_or_s_pp_systems in acquisition_pairings.values():
        boom_unoccupied_system = PopulatedGalaxySystems.from_powerplay_system(boom_unoccupied_pp_system)
        tmp = [PopulatedGalaxySystems.from_powerplay_system(system) for system in f_or_s_pp_systems]
        f_or_s_systems = [system for system in tmp if system is not None]

        if boom_unoccupied_system is not None and len(f_or_s_systems) > 0:
            acquirable_systems.append(
                AcquisitionSystemPairings(
                    boom_unoccupied_system,
                    f_or_s_systems,
                )
            )

    # Filter for unoccupied systems above minimum population and has at least one valid hotspot
    acquirable_systems = [
        acquirable_system
        for acquirable_system in acquirable_systems
        if acquirable_system.unoccupied_system.population > args.min_population
        and acquirable_system.has_valid_hotspot_ring(args.target_commodities)
    ]

    # Sort by distance
    acquirable_systems.sort(
        reverse=True,
        key=lambda pair: args.current_coords.distance_to(pair.unoccupied_system.coords),
    )

    return acquirable_systems


def run(args: argparse.Namespace) -> None:
    systems_count = 0
    stations_count = 0
    for acquisition_pair in find_acquirable_systems(args):
        acquiring_systems = acquisition_pair.acquiring_systems
        target_system = acquisition_pair.unoccupied_system
        all_stations = target_system.get_stations_with_services(["Market"])

        stations = [
            station
            for station in all_stations
            if station.has_commodities(args.target_commodities, require_all=False)
            and station.has_minimum_landing_pad(args.min_landing_pad_size)
            and station.has_min_data_age_days(args.min_market_data_age)
        ]

        if stations:
            logger.info("")
            logger.info("")
            logger.info("===============================")
            logger.info("=        ACQUISITION?         =")
            for system in acquiring_systems:
                ring_hotspots = system.get_hotspot_rings(args.target_commodities)
                if ring_hotspots:
                    logger.info("===============================")
                    logger.info("====== ACQUIRING SYSTEM =======")
                    logger.info("===============================")
                    logger.info(
                        f"Name: {system.name} (Distance: {args.current_coords.distance_to(system.coords):.2f}LY)"
                    )
                    logger.info(f"Last Updated: {get_time_since(system.date)}")

                    for ring_name, hotspots in ring_hotspots.items():
                        logger.info(f"++ {ring_name} ++")
                        for mineral_type, hotspot_count in hotspots.items():
                            logger.info(f"  > {mineral_type}: {hotspot_count} Hotspots")

            logger.info("")
            logger.info("====== UNOCCUPIED SYSTEM ======")
            logger.info(
                f"Name: {target_system.name} (Distance {args.current_coords.distance_to(target_system.coords):.2f}LY)"
            )
            logger.info(f"Last Updated: {get_time_since(target_system.date)}")
            logger.info(f"Population: {target_system.population:,}")
            logger.info(pformat(max(target_system.factions, key=lambda f: f.influence)))

            logger.trace(pformat(target_system, depth=2))

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
    args = parse_args()
    configure_logger(args)
    with Timer("Script", True):
        run(args)
