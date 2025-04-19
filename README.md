# Elite Dangerous Related Data Things

### Usage
- `./download_dump_data && ./import_dump_data`
- `./find_potential_acquisition_system_stations`
- `./find_potential_reinforcement_system_stations`

### Bottlenecks
- Data size of a single system is massive
  - Returning a whole system takes up massive bandwidth
  - Long running queries (~30 seconds for returning ~120 systems) are largely because of data transfer time - not compute time
  - Need more fine-grained tables and support for partially returned data (Eg, return bodies but only name, reserve level, and ring information in each object)