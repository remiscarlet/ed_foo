# Data comes from Spansh and EDSM dumps
from pathlib import Path

PWD = Path.cwd()
REPO_ROOT = Path(__file__).parent
REL_PATH = PWD.relative_to(REPO_ROOT)

DATA_DIR = REL_PATH / "data"

# GALAXY_POPULATED = DATA_DIR / "galaxy_populated.truncated.json"
GALAXY_POPULATED = DATA_DIR / "galaxy_populated.json"

GALAXY_POPULATED_BY_SYSTEM_NAME = DATA_DIR / "galaxy_populated_by_system_name.json"
GALAXY_POPULATED_IN_PP_RANGE = DATA_DIR / "galaxy_populated_in_pp_range.json"
GALAXY_POPULATED_IN_NK_PP_RANGE = DATA_DIR / "galaxy_populated_in_nakato_kaine_pp_range.json"
GALAXY_POPULATED_IN_NK_BOOM_UNOCCUPIED_PP_RANGE = DATA_DIR / "galaxy_populated_in_nakato_kaine_boom_unoccupied.json"
# GALAXY_POPULATED_IN_NK_BOOM_UNOCCUPIED_PP_RANGE = DATA_DIR / "debug.json"

POWERPLAY_SYSTEMS = DATA_DIR / "powerPlay.json"

