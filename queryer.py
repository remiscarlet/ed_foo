import pprint

from powerplay_systems import PowerplaySystems

powerplay_systems = PowerplaySystems()
nk_boom_unoccupied_systems = powerplay_systems.get_systems({
    "power": ["Nakato Kaine"],
    "powerState": ["Unoccupied"],
    "state": ["Boom"]
})

nk_s_and_f_systems = powerplay_systems.get_systems({
    "power": ["Nakato Kaine"],
    "powerState": ["Fortified", "Stronghold"],
})

for s_or_f_system in nk_s_and_f_systems:
    for boom_unoccupied_system in nk_boom_unoccupied_systems:
        if s_or_f_system.is_in_influence_range(boom_unoccupied_system):
            pprint.pprint(boom_unoccupied_system)

# populated_galaxy_systems = PopulatedGalaxySystems()
# systems = populated_galaxy_systems.get_target_nakato_kaine_systems()

# for system_name, system in systems.items():
#     print("")
#     print("==============================")
#     pprint.pprint(system_name)
#     pprint.pprint(system, depth=2)
#     print(system)
#     break