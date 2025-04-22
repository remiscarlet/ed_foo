# Data comes from Spansh and EDSM dumps
from pathlib import Path

PWD = Path.cwd()
REPO_ROOT = Path(__file__).parent.parent
REL_ROOT_PATH = PWD.relative_to(REPO_ROOT)

LOG_DIR = REL_ROOT_PATH / "logs"
DEFAULT_LOG_LEVEL = "INFO"

DATA_DIR = REL_ROOT_PATH / "data"

DB_DATA_PATH = DATA_DIR / "processed_data.db"
# GALAXY_POPULATED = DATA_DIR / "galaxy_populated.truncated.json"
GALAXY_POPULATED_JSON = DATA_DIR / "galaxy_populated.json"
GALAXY_POPULATED_JSON_GZ = DATA_DIR / "galaxy_populated.json.gz"
POWERPLAY_SYSTEMS = DATA_DIR / "powerPlay.json"


GALAXY_POPULATED_JSON_URL = "https://downloads.spansh.co.uk/galaxy_populated.json.gz"
