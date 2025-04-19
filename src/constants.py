# Data comes from Spansh and EDSM dumps
from pathlib import Path

PWD = Path.cwd()
REPO_ROOT = Path(__file__).parent
REL_PATH = PWD.relative_to(REPO_ROOT)

DATA_DIR = REL_PATH / "data"

DB_DATA_PATH = DATA_DIR / "processed_data.db"
# GALAXY_POPULATED = DATA_DIR / "galaxy_populated.truncated.json"
GALAXY_POPULATED = DATA_DIR / "galaxy_populated.json"
POWERPLAY_SYSTEMS = DATA_DIR / "powerPlay.json"
