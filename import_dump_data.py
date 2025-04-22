#!python

from src.constants import GALAXY_POPULATED_JSON
from src.populated_galaxy_systems_importer import PopulatedGalaxySystemsImporter

filterer = PopulatedGalaxySystemsImporter(GALAXY_POPULATED_JSON)
filterer.filter_and_import_systems()
