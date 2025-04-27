#!python

from src.common.constants import (
    GALAXY_POPULATED_JSON,
    GALAXY_POPULATED_JSON_GZ,
    GALAXY_POPULATED_JSON_URL,
)
from src.common.utils import download_file, ungzip


def download_spansh_dump():
    GALAXY_POPULATED_JSON_GZ.parent.mkdir(parents=True, exist_ok=True)

    download_file(GALAXY_POPULATED_JSON_URL, GALAXY_POPULATED_JSON_GZ)
    ungzip(GALAXY_POPULATED_JSON_GZ, GALAXY_POPULATED_JSON)
