# Data comes from Spansh and EDSM dumps
from pathlib import Path

import yaml

PWD = Path.cwd()
REPO_ROOT = Path(__file__).parent.parent.parent
REL_ROOT_PATH = PWD.relative_to(REPO_ROOT)

LOG_DIR = REL_ROOT_PATH / "logs"
DEFAULT_LOG_LEVEL = "INFO"

# Data dir
DATA_DIR = REL_ROOT_PATH / "data"

DB_DATA_PATH = DATA_DIR / "processed_data.db"
# GALAXY_POPULATED_JSON = DATA_DIR / "galaxy_populated.first100.json"
# GALAXY_POPULATED_JSON = DATA_DIR / "galaxy_populated.truncated.json"
GALAXY_POPULATED_JSON = DATA_DIR / "galaxy_populated.json"
GALAXY_POPULATED_JSON_GZ = DATA_DIR / "galaxy_populated.json.gz"
POWERPLAY_SYSTEMS = DATA_DIR / "powerPlay.json"

GALAXY_POPULATED_JSON_URL = "https://downloads.spansh.co.uk/galaxy_populated.json.gz"

# Metadata Dir
METADATA_DIR = REL_ROOT_PATH / "metadata"
METADATA_SCHEMAS_DIR = METADATA_DIR / "schemas"
ENUMS_SCHEMA = METADATA_SCHEMAS_DIR / "enums.schema.json"
COMMODITIES_SCHEMA = METADATA_SCHEMAS_DIR / "commodities.schema.json"
COMMODITIES_YAML_FMT = "commodities.*.yaml"

# Others
SQL_DIR = REL_ROOT_PATH / "src" / "adapters" / "persistence" / "postgresql" / "sql"


CONFIG_FILE = REL_ROOT_PATH / "config.yaml"
if not CONFIG_FILE.exists():
    raise RuntimeError(
        "config.yaml could not be found! Please create one while using config.example.yaml as an example."
    )

with CONFIG_FILE.open("r") as file:
    data = yaml.safe_load(file)
    DISCORD_BOT_TOKEN = data.get("discord_bot", {}).get("token", "NO_TOKEN")
