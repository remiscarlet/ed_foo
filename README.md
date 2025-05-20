# EKAINE
###### (Enhanced Knowledge Analysis and Insights Notification Engine)

EKAINE delivers a fully schematized and enriched database optimized for powerful, flexible querying—surpassing the capabilities of existing tools. Its most powerful feature is the seamless cross-querying of system, station, body, and market data through standard SQL.

## What Is

EKAINE is a **data ingestion, enrichment, analysis, and workflow automation system** for *Elite Dangerous* game data.

It collects, processes, and exposes structured data from external sources like **EDDN** (Live), **Spansh** (Dumps), and **EDSM** (Dumps), and allows interaction with insights via:
- Discord bots
- Webhooks
- CLI tools
- REST APIs (Maybe)

### Features
Most features are focused on Powerplay 2.0 mechanics.

Major features are split into "queries" and "alerts"

#### Queries (All queries have configurable arguments/filters):
- Get Hotspots for System
- Get Top N Commodity Prices at Stations for System
- Get Top Mining Reinforcement Routes Globally
- Get Mining Reinforcement Routes for System
- Get Mining Acqusition Routes for System

#### Alerts (Coming Soon):
- Notify When System Enters Boom (Filterable)
- Notify Systems Being Undermined
- Notify System Control Point Thresholds ('50%', '75%', etc to 'Min Control Score', 'Fortified', etc)

Queries and Alerts are made by querying a fully schematized timescale/PostgreSQL database. Timescale allows time-series queries and alerts while the standard PG allows stateful queries and alerts.

Many more to come.

## Usage
### Pre-req
- Install [Poetry](https://python-poetry.org/docs/#installation)
- `git clone` this repo
- If you already have a Spansh `galaxy_populated.json` data dump, add it to `data/` with default filename
  - If so, `make import-spansh` instead of `make run-pipeline`

### Initial Setup/Database Hydration
```
make setup
make run-pipeline
```

### EDDN Listener
```
make eddn-listener
```

### Adhoc SQL Queries
```
make pg-shell
```

### Discord Integration
```
make discord-bot
```

![Example](docs/discord_get-top-reinf-mining-routes.png)
![Example](docs/discord_get-mining-expandable.png)
![Example](docs/discord_get-top-commodities.png)
![Example](docs/discord_get-hotspots.png)

## Dev Stuff
- Linters and type checkers run on commit via `pre-commit`

To run the linter, fix lint issues, and type check:
```
make lint-fix-check
```

### Interesting Locations (For Now)
- `src/interfaces/discord/bot.py`
  - Discord bot entrypoint
- `src/postgresql/`
  - Any and all database-specific things like SQL files, sqlalchemy schemas, etc
  - Except DB migrations.
- `src/alembic/`
  - Stores all DB migrations
- `src/ingestion/`
  - Data ingestion logic
  - Spansh dump data DL/import pipeline
  - WIP EDDN live update listener

### DB Schema
- See https://dbdiagram.io/d/EKAINE-680e5f821ca52373f58ba72d
![DB Schema](docs/schema.png)
