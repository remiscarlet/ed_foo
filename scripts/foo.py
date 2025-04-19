import json
import pathlib
import pprint
from constants import GALAXY_POPULATED


def __load_data_dump(dump_file: str):
    p_in = pathlib.Path(dump_file)

    fields = {}
    with p_in.open("r") as f:
        systems = json.load(f)
        for system in systems:
            for field in system.keys():
                if field not in fields:
                    fields[field] = 0
                fields[field] += 1

    pprint.pprint(fields)


__load_data_dump(GALAXY_POPULATED)
