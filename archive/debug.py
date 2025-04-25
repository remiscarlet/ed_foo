#!python

from argparse import Namespace
from pprint import pprint

from src.logging import configure_logger
from src.populated_galaxy_systems import PopulatedGalaxySystems

configure_logger(args=Namespace(verbosity=1))

DEBUG_SYSTEM = "Juragura"
system = PopulatedGalaxySystems().get_system(DEBUG_SYSTEM)
pprint(system, depth=1)
pprint(system.factions)

if system is not None:
    for station in system.stations:
        if station.name != "Stephenson Hub":
            continue
        # pprint(station.market or [], depth=2)
