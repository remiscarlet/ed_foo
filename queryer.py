import pprint
from typing import List, Tuple

from ed_types import AcquisitionSystemPairing, Coordinates, Minerals, PowerplaySystem
from populated_galaxy_systems import PopulatedGalaxySystems
from powerplay_systems import PowerplaySystems
from timer import Timer

MIN_LANDING_PAD = "medium"  # "large" # "small"
TARGET_COMMODITIES = [Minerals.Platinum.value, Minerals.Monazite.value]
MAX_DISTANCE = 250  # LY
MIN_POPULATION = 100000
# -5 / 117.84 / 127.69
CURRENT_COORDS = Coordinates(
    x=-5,
    y=117.84,
    z=127.69,
)
DEBUG = False  # True


class Queryer:
    def __init__(self):
        timer = Timer("Queryer.__init__()")

        self.powerplay_systems = PowerplaySystems.get_powerplay_systems()
        self.populated_galaxy_systems = PopulatedGalaxySystems()
        pprint.pprint(self.populated_galaxy_systems.get_system("HIP 23692 A"))

        timer.end()

    def find_acquirable_systems(self):
        # Unoccupied systems in Boom state under Nakato Kaine influence sphere
        nk_boom_unoccupied_systems = self.powerplay_systems.get_systems(
            {"power": ["Nakato Kaine"], "powerState": ["Unoccupied"], "state": ["Boom"]}
        )#[5:10]

        # Fortified or Stronghold systems under Nakato Kaine control
        nk_f_or_s_systems = self.powerplay_systems.get_systems(
            {
                "power": ["Nakato Kaine"],
                "powerState": ["Fortified", "Stronghold"],
            }
        )

        # Get all "acquisition pairs" to hydrate from the sqlite
        # We want to do it in one query to minimize query overhead
        system_pairs_to_hydrate: List[Tuple[PowerplaySystem, PowerplaySystem]] = []
        for boom_unoccupied_system in nk_boom_unoccupied_systems:
            for f_or_s_system in nk_f_or_s_systems:
                if (
                    f_or_s_system.is_in_influence_range(boom_unoccupied_system)
                    and CURRENT_COORDS.distance_to(boom_unoccupied_system.coords)
                    <= MAX_DISTANCE
                ):
                    system_pairs_to_hydrate.append(
                        (f_or_s_system, boom_unoccupied_system)
                    )

        system_names_to_hydrate = set(
            [system.name for pair in system_pairs_to_hydrate for system in pair]
        )
        db_hydration_timer = Timer(
            f"find_acquirable_systems - db_hydration_timer - {len(system_names_to_hydrate)} systems"
        )
        self.populated_galaxy_systems.get_systems(list(system_names_to_hydrate))
        db_hydration_timer.end()

        acquirable_systems: List[AcquisitionSystemPairing] = [
            AcquisitionSystemPairing(
                self.populated_galaxy_systems.from_powerplay_system(f_or_s_system),
                self.populated_galaxy_systems.from_powerplay_system(
                    boom_unoccupied_system
                ),
            )
            for (f_or_s_system, boom_unoccupied_system) in system_pairs_to_hydrate
        ]

        # Filter for unoccupied systems above minimum population and has at least one valid hotspot
        acquirable_systems = [
            acquirable_system
            for acquirable_system in acquirable_systems
            if acquirable_system.unoccupied_system is not None
            and acquirable_system.unoccupied_system.population > MIN_POPULATION
            # and acquirable_system.acquiring_system.get_hotspot_rings(
            #     [Minerals.Platinum, Minerals.Monazite]
            # )
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
            acquiring_system = acquisition_pair.acquiring_system
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
                print("====== UNOCCUPIED SYSTEM ======")
                print(
                    f"Distance: {CURRENT_COORDS.distance_to(target_system.coords):.2f}LY"
                )
                print(f"Name: {target_system.name}")
                print(f"Updated: {target_system.date}")
                print(f"Population: {target_system.population}")
                print("")
                print("====== ACQUIRING SYSTEM ======")
                print(
                    f"Distance: {CURRENT_COORDS.distance_to(acquiring_system.coords):.2f}LY"
                )
                print(f"Name: {acquiring_system.name}")
                print(f"Updated: {acquiring_system.date}")

                for ring_name, hotspots in acquiring_system.get_hotspot_rings(
                    [Minerals.Platinum, Minerals.Monazite]
                ).items():
                    print(f"++ {ring_name} ++")
                    for mineral_type, hotspot_count in hotspots.items():
                        print(f"  > {mineral_type}: {hotspot_count} Hotspots")
                if DEBUG:
                    pprint.pprint(acquiring_system, depth=2)

            for station in stations:
                print("")
                print("== UNOCCUPIED SYSTEM STATION")
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


if __name__ == "__main__":
    timer = Timer("Script")
    Queryer().run()
    timer.end()
