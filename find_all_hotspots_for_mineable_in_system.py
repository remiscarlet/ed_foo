#!python

import argparse
import textwrap

from src.argparse_actions import StoreMineableCommodities, StoreSystemNameWithCoords
from src.logging import configure_logger, get_logger
from src.populated_galaxy_systems import PopulatedGalaxySystems
from src.timer import Timer
from src.types import Mineables

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    argparser = argparse.ArgumentParser(
        __name__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
    Looks for hotspots of the target commodities in the provided system.
    """
        ),
    )
    argparser.add_argument(
        "--mineable",
        dest="mineables",
        action=StoreMineableCommodities,
        type=Mineables,
        help="Mineable commodities to target",
        choices=list(Mineables),
    )
    argparser.add_argument(
        "--system",
        action=StoreSystemNameWithCoords,
        type=str,
        help="Current system name. If we don't know about this system, will default to Sol coords",
        default="Sol",
    )
    argparser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0)

    return argparser.parse_args()


def run(args: argparse.Namespace) -> None:
    system = PopulatedGalaxySystems.get_system(args.system)
    if system is None:
        raise Exception(f"Did not know about the system '{args.system}'!")

    ring_hotspots = system.get_hotspot_rings(args.mineables)

    logger.info("")
    logger.info("====== SYSTEM ======")
    logger.info(f"Name: {system.name}")
    logger.info(f"Target Mineables: {[mineable.value for mineable in args.mineables]}")
    logger.info("")
    if not ring_hotspots:
        logger.info("!! No valid rings found for target mineables!")
    for ring_name, hotspots in ring_hotspots.items():
        logger.info(f"++ {ring_name} ++")
        for mineable_type, hotspot_count in hotspots.items():
            logger.info(f"  > {mineable_type}: {hotspot_count} Hotspots")


if __name__ == "__main__":
    with Timer("Script", True):
        args = parse_args()
        configure_logger(args)
        run(args)
