import pprint
from typing import List

from constants import GALAXY_POPULATED_IN_NK_BOOM_UNOCCUPIED_PP_RANGE
from ed_types import AcquisitionSystemPairing, Coordinates, PowerplaySystem
from populated_galaxy_systems import PopulatedGalaxySystems
from powerplay_systems import PowerplaySystems

MIN_LANDING_PAD = "medium"  # "large" # "small"
TARGET_COMMODITIES = ["Platinum", "Monazite"]
MAX_DISTANCE = 250  # LY
MIN_POPULATION = 100000
# -5 / 117.84 / 127.69
CURRENT_COORDS = Coordinates(
    x=-5,
    y=117.84,
    z=127.69,
)
DEBUG = False  # True

populated_galaxy_systems = PopulatedGalaxySystems()
pprint.pprint(populated_galaxy_systems.get_system("HIP 23692 A"))

powerplay_systems = PowerplaySystems.get_powerplay_systems()
nk_boom_unoccupied_systems = powerplay_systems.get_systems(
    {"power": ["Nakato Kaine"], "powerState": ["Unoccupied"], "state": ["Boom"]}
)

nk_f_and_s_systems = powerplay_systems.get_systems(
    {
        "power": ["Nakato Kaine"],
        "powerState": ["Fortified", "Stronghold"],
    }
)

acquirable_systems: List[AcquisitionSystemPairing] = [
    AcquisitionSystemPairing(
        f_or_s_system,
        populated_galaxy_systems.from_powerplay_system(boom_unoccupied_system),
    )
    for boom_unoccupied_system in nk_boom_unoccupied_systems
    for f_or_s_system in nk_f_and_s_systems
    if f_or_s_system.is_in_influence_range(boom_unoccupied_system)
    and CURRENT_COORDS.distance_to(boom_unoccupied_system.coords) <= MAX_DISTANCE
]
acquirable_systems = [
    acquirable_system
    for acquirable_system in acquirable_systems
    if acquirable_system.unoccupied_system is not None
]

systems_count = 0
stations_count = 0

acquirable_systems.sort(
    reverse=True,
    key=lambda pair: CURRENT_COORDS.distance_to(pair.unoccupied_system.coords),
)
for acquisition_pair in acquirable_systems:
    system = acquisition_pair.unoccupied_system
    if system.population < MIN_POPULATION:
        continue

    pprint.pprint(system, depth=1)

    all_stations = system.get_stations_with_services(["Market"])

    stations = [
        station
        for station in all_stations
        if station.has_commodities(TARGET_COMMODITIES, require_all=False)
        and station.has_minimum_landing_pad(MIN_LANDING_PAD)
    ]

    if stations:
        print("")
        print("====================")
        print("====== SYSTEM ======")
        print(f"Distance: {CURRENT_COORDS.distance_to(system.coords):.2f}LY")
        print(f"Name: {system.name}")
        print(f"Updated: {system.date}")
        print(f"Population: {system.population}")
        if DEBUG:
            pprint.pprint(system, depth=2)

    for station in stations:
        print("")
        print("== STATION")
        print(f">> Name: {station.name}")
        print(f">> Updated: {station.updateTime}")
        print(f">> Distance: {station.distanceToArrival:.2f}LS")
        print(f">> Economies: {station.economies}")
        print(f">> Is Settlement: {'No' if station.longitude is None else 'Yes'}")
        for commodity in TARGET_COMMODITIES:
            print(
                f"  !! {commodity} !! {pprint.pformat(station.get_commodity_price(commodity))}"
            )
        if DEBUG:
            pprint.pprint(station, depth=2)

    systems_count += 1
    stations_count += len(stations)

print("")
print("=============")
print(f"Systems: {systems_count}")
print(f"Stations: {stations_count}")
