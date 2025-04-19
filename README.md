# Elite Dangerous Related Data Things

Hypothesis: There are systems that have elevated commodity prices but we don't know about them because of data staleness.

Faction state (Boom) information is revealed when entering a system, which is much more likely than exact
commodity prices which requires a CMDR to dock at a specific station.

As such, there exists a time delta between freshness of faction states and known market prices.
This script tries to analyze this delta for potential stations to check prices at for advantageous PP2.0 play

<sub>Spoiler: Turns out the hypothesis is probably not-correct-enough to be useful. There's also faction state data staleness concerns.</sub>

### Usage
- `./download_dump_data && ./import_dump_data`
- `./find_potential_acquisition_system_stations`
- `./find_potential_reinforcement_system_stations`

### Bottlenecks
- Data size of a single system is massive
  - Returning a whole system takes up massive bandwidth
  - Long running queries (~30 seconds for returning ~120 systems) are largely because of data transfer time - not compute time
  - Need more fine-grained tables and support for partially returned data (Eg, return bodies but only name, reserve level, and ring information in each object)

## Example Output
- `./find_potential_acquisition_system_stations`
```
===============================
=        ACQUISITION?         =
===============================
====== ACQUIRING SYSTEM =======
===============================
Name: HIP 62118 (Distance: 154.12LY)
Last Updated: 2 Days, 3 Hours Ago
++ HIP 62118 A 1 A Ring ++
  > Monazite: 3 Hotspots
++ HIP 62118 A 2 A Ring ++
  > Platinum: 3 Hotspots
  > Monazite: 3 Hotspots
++ HIP 62118 A 2 B Ring ++
  > Monazite: 2 Hotspots

====== UNOCCUPIED SYSTEM ======
Name: Juragura (Distance 172.53LY)
Last Updated: 1 Day, 4 Hours Ago
Population: 235,474
PlayerMinorFaction(name='Starstone Enterprises',
                   influence=0.646707,
                   government='Cooperative',
                   allegiance='Independent',
                   state='Boom')

== STATION
>> Name: Cook Refinery (22.73LS)
>> Last Updated: 2 Weeks, 6 Days Ago
>> Economies: {'Refinery': 100.0}
>> Controlling Faction: Juragura Exchange (State: None)
  !! Monazite !! Last Known CommodityPrice(buyPrice=0, demand=47, sellPrice=196375, supply=0)
  !! Platinum !! Last Known CommodityPrice(buyPrice=32400, demand=0, sellPrice=32398, supply=0)

== STATION
>> Name: Dedman Landing (144.03LS)
>> Last Updated: 6 Weeks, 5 Days, 3 Hours Ago
>> Economies: {'Terraforming': 100.0}
>> Controlling Faction: Starstone Enterprises (State: None)
  !! Platinum !! Last Known CommodityPrice(buyPrice=0, demand=136, sellPrice=54937, supply=0)
```

- `./find_potential_reinforcement_system_stations`
```
===============================
=        REINFORCEMENT?       =
=========== SYSTEM ============
Name: Selkana (Fortified)
Distance: 131.60LY
Last Updated: 1 Day, 2 Hours Ago
Population: 1,614,530,543
Controlling Faction: PlayerMinorFaction(name='Selkana Labour',
                   influence=0.521956,
                   government='Democracy',
                   allegiance='Independent',
                   state='Boom')
++ Selkana 8 A Ring ++
  > Monazite: 1 Hotspots

== STATION
>> Name: Donoso's Reception (1728.93LS)
>> Last Updated: 194 Weeks, 1 Day, 10 Hours Ago
>> Economies: {'Tourism': 100.0}
>> Controlling Faction: Selkana Labour (State: None)
  !! Monazite !! Last Known CommodityPrice(buyPrice=0, demand=9, sellPrice=189212, supply=0)
  !! Platinum !! Last Known CommodityPrice(buyPrice=0, demand=704, sellPrice=58114, supply=0)

== STATION
>> Name: Gaffney Enterprise (771.16LS)
>> Last Updated: 4 Weeks, 6 Days, 4 Hours Ago
>> Economies: {'Extraction': 100.0}
>> Controlling Faction: Union of Jath for Equality (State: None)
  !! Monazite !! Last Known CommodityPrice(buyPrice=113666, demand=0, sellPrice=112540, supply=0)
  !! Platinum !! Last Known CommodityPrice(buyPrice=34007, demand=0, sellPrice=33670, supply=0)
```
