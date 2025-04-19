import pprint
from typing import Dict, List, Tuple

from ed_types import AcquisitionSystemPairings, Coordinates, Minerals, PowerplaySystem
from populated_galaxy_systems import PopulatedGalaxySystems
from powerplay_systems import PowerplaySystems
from timer import Timer

MAX_SYSTEM_DATA_AGE_IN_DAYS = 2
MIN_LANDING_PAD = "medium"  # "large" # "small"
TARGET_COMMODITIES = [Minerals.Platinum.value, Minerals.Monazite.value]
MAX_DISTANCE = 250  # LY
MIN_POPULATION = 100000
# 126.91 / 41.63 / 28.66
CURRENT_COORDS = Coordinates(
    x=50.28, # Hydrae Sector TZ-P b5-5
    y=82.81,
    z=115.88,
    # x=-5, # HIP 75521
    # y=117.84,
    # z=28.66,
)
DEBUG = False  # True


class Queryer:
    def __init__(self):
        timer = Timer("Queryer.__init__()")

        self.powerplay_systems = PowerplaySystems()
        self.populated_galaxy_systems = PopulatedGalaxySystems()

        pprint.pprint(self.populated_galaxy_systems.get_system("HIP 23692 A"))

        timer.end()

    def find_acquirable_systems(self):
        # Unoccupied systems in Boom state under Nakato Kaine influence sphere
        boom_nk_unoccupied_systems = self.powerplay_systems.get_acquisition_systems(
            "Nakato Kaine",
            ["Boom"],
            MAX_SYSTEM_DATA_AGE_IN_DAYS,
        )  # [5:10]

        # Fortified or Stronghold systems under Nakato Kaine control
        nk_f_or_s_systems = self.powerplay_systems.get_reinforcement_systems(
            "Nakato Kaine",
            ["Fortified", "Stronghold"],
        )

        # Get all "acquisition pairs" to hydrate from the sqlite
        # We want to do it in one query to minimize query overhead
        acquisition_pairings: Dict[
            str, Tuple[PowerplaySystem, List[PowerplaySystem]]
        ] = {}
        for target_sys in boom_nk_unoccupied_systems:
            for src_sys in nk_f_or_s_systems:
                if (
                    src_sys.is_in_influence_range(target_sys)
                    and CURRENT_COORDS.distance_to(target_sys.coords)
                    <= MAX_DISTANCE
                ):
                    if target_sys.name not in acquisition_pairings:
                        acquisition_pairings[target_sys.name] = (target_sys, [])
                    acquisition_pairings[target_sys.name][1].append(src_sys)

        to_hydrate = set()
        for target_sys, acquisition_systems in acquisition_pairings.values():
            to_hydrate.add(target_sys.name)
            to_hydrate.update(map(lambda sys: sys.name, acquisition_systems))

        db_hydration_timer = Timer(
            f"find_acquirable_systems - db_hydration_timer - {len(to_hydrate)} systems"
        )
        self.populated_galaxy_systems.get_systems(list(to_hydrate))
        db_hydration_timer.end()

        acquirable_systems: List[AcquisitionSystemPairings] = [
            AcquisitionSystemPairings(
                self.populated_galaxy_systems.from_powerplay_system(
                    boom_unoccupied_system
                ),
                [
                    self.populated_galaxy_systems.from_powerplay_system(system)
                    for system in f_or_s_systems
                ],
            )
            for (
                boom_unoccupied_system,
                f_or_s_systems,
            ) in acquisition_pairings.values()
        ]

        # Filter for unoccupied systems above minimum population and has at least one valid hotspot
        acquirable_systems = [
            acquirable_system
            for acquirable_system in acquirable_systems
            if acquirable_system.unoccupied_system.population > MIN_POPULATION
            and acquirable_system.has_valid_hotspot_ring(
                [Minerals.Platinum, Minerals.Monazite]
            )
        ]

        # Sort by distance
        acquirable_systems.sort(
            reverse=True,
            key=lambda pair: CURRENT_COORDS.distance_to(pair.unoccupied_system.coords),
        )

        return acquirable_systems

    def run(self):
        systems_count = 0
        stations_count = 0
        for acquisition_pair in self.find_acquirable_systems():
            acquiring_systems = acquisition_pair.acquiring_systems
            target_system = acquisition_pair.unoccupied_system
            all_stations = target_system.get_stations_with_services(["Market"])

            stations = [
                station
                for station in all_stations
                if station.has_commodities(TARGET_COMMODITIES, require_all=False)
                and station.has_minimum_landing_pad(MIN_LANDING_PAD)
            ]

            if stations:
                print("")
                print("===============================")
                for system in acquiring_systems:
                    print("====== ACQUIRING SYSTEM ======")
                    print(
                        f"Distance: {CURRENT_COORDS.distance_to(system.coords):.2f}LY"
                    )
                    print(f"Name: {system.name}")
                    print(f"Updated: {system.date}")

                    for ring_name, hotspots in system.get_hotspot_rings(
                        [Minerals.Platinum, Minerals.Monazite]
                    ).items():
                        print(f"++ {ring_name} ++")
                        for mineral_type, hotspot_count in hotspots.items():
                            print(f"  > {mineral_type}: {hotspot_count} Hotspots")

                print("")
                print("====== UNOCCUPIED SYSTEM ======")
                print(
                    f"Distance: {CURRENT_COORDS.distance_to(target_system.coords):.2f}LY"
                )
                print(f"Name: {target_system.name}")
                print(f"Updated: {target_system.date}")
                print(f"Population: {target_system.population}")
                print(f"Factions: {pprint.pformat(target_system.factions)}")
                if DEBUG:
                    pprint.pprint(target_system, depth=2)

            for station in stations:
                print("")
                print("== STATION")
                print(f">> Name: {station.name} ({station.distanceToArrival:.2f}LS)")
                print(f">> Updated: {station.updateTime.isoformat()}")
                print(f">> Economies: {station.economies}")
                print(f">> Controlling Faction Name: {pprint.pformat(station.controllingFaction)}")
                print(f">> Controlling Faction State: {pprint.pformat(station.controllingFactionState)}")
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


if __name__ == "__main__":
    timer = Timer("Script")
    Queryer().run()
    timer.end()
