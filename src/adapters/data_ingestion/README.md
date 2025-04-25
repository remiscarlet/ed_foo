## What
- Dataclasses here should only represent "schema definitions" so we can import data sources - DTOs.

## TODO
- Should eventually have no methods on the dataclasses
    - Load from dumps (this) -> converter (`src/dataconverters/`) -> orm (`src/orm/`)