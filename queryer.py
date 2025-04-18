import pprint
from typing import List

from constants import GALAXY_POPULATED_IN_NK_BOOM_UNOCCUPIED_PP_RANGE, GALAXY_POPULATED_IN_NK_PP_RANGE
from ed_types import Coordinates, PowerplaySystem
from populated_galaxy_systems import PopulatedGalaxySystems
from powerplay_systems import PowerplaySystems

TARGET_COMMODITIES = ["Platinum", "Monazite"]
MAX_DISTANCE = 250 # LY
MIN_POPULATION = 100000
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

populated_galaxy_systems = PopulatedGalaxySystems(GALAXY_POPULATED_IN_NK_BOOM_UNOCCUPIED_PP_RANGE, True)

systems_count = 0
stations_count = 0

acquirable_systems.sort(key=lambda system: CURRENT_COORDS.distance_from(system.coords))
for pp_system in acquirable_systems:
    distance = CURRENT_COORDS.distance_from(pp_system.coords)
    if distance > MAX_DISTANCE:
        continue

    system = populated_galaxy_systems.get_system(pp_system.name)
    if system.population < MIN_POPULATION:
        continue

    print("====== SYSTEM ======")
    print(f"Distance: {distance:.2f}LY")
    pprint.pprint(system, depth=1)

    all_stations = system.get_stations_with_services(["Market"])
    stations = list(filter(lambda station: station.has_commodities(TARGET_COMMODITIES), all_stations))
    for station in stations:
        print("")
        print("== STATION")
        print(f">> Name: {station.name}")
        print(f">> Updated: {station.updateTime}")
        print(f">> Landing Pads: {station.landingPads}")
        print(f">> Economies: {station.economies}")
        print(f">> Is Settlement: {'No' if station.longitude is None else 'Yes'}")
        for commodity in TARGET_COMMODITIES:
            print(f"  >> COMMODITY: {commodity} <<")
            pprint.pprint(station.get_commodity_price(commodity))

    systems_count += 1
    stations_count += len(stations)

print("")
print("=============")
print(f"Systems: {systems_count}")
print(f"Stations: {stations_count}")
