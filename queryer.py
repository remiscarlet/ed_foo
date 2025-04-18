import pprint
from typing import List

from constants import GALAXY_POPULATED_IN_NK_PP_RANGE
from ed_types import Coordinates, PowerplaySystem
from populated_galaxy_systems import PopulatedGalaxySystems
from powerplay_systems import PowerplaySystems

MAX_DISTANCE = 100 # LY
# -5 / 117.84 / 127.69
CURRENT_COORDS = Coordinates(
    x = -5,
    y = 117.84,
    z = 127.69,
)

powerplay_systems = PowerplaySystems.get_powerplay_systems()
nk_boom_unoccupied_systems = powerplay_systems.get_systems({
    "power": ["Nakato Kaine"],
    "powerState": ["Unoccupied"],
    "state": ["Boom"]
})

nk_s_and_f_systems = powerplay_systems.get_systems({
    "power": ["Nakato Kaine"],
    "powerState": ["Fortified", "Stronghold"],
})

acquirable_systems: List[PowerplaySystem] = []
for s_or_f_system in nk_s_and_f_systems:
    for boom_unoccupied_system in nk_boom_unoccupied_systems:
        if s_or_f_system.is_in_influence_range(boom_unoccupied_system):
            acquirable_systems.append(boom_unoccupied_system)

populated_galaxy_systems = PopulatedGalaxySystems()
populated_galaxy_systems.load_processed_dump_file(GALAXY_POPULATED_IN_NK_PP_RANGE)

acquirable_systems.sort(key=lambda system: CURRENT_COORDS.distance_from(system.coords))
for system in acquirable_systems:
    distance = CURRENT_COORDS.distance_from(system.coords)
    if distance > MAX_DISTANCE:
        break

    print("=============")
    print(f"Distance: {distance:.2f}LY")
    pprint.pprint(system)

    pprint.pprint(populated_galaxy_systems.get_stations(system.name))

    break



# populated_galaxy_systems = PopulatedGalaxySystems()
# systems = populated_galaxy_systems.get_target_nakato_kaine_systems()

# for system_name, system in systems.items():
#     print("")
#     print("==============================")
#     pprint.pprint(system_name)
#     pprint.pprint(system, depth=2)
#     print(system)
#     break