import argparse
import pprint

from src.ed_types import Coordinates
from src.populated_galaxy_systems import PopulatedGalaxySystems


class StoreSystemNameWithCoords(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        system = PopulatedGalaxySystems.get_system(values)
        coords = Coordinates(0, 0, 0) if system is None else system.coords
        setattr(namespace, "current_coords", coords)
        pprint.pprint(namespace)
