# ED Foo (Enhanced Knowledge Analysis and Insights Notification Engine)

<sub>Extremely WIP — initial refactor in progress.</sub>
---

## Usage
### Pre-req
- Install [Poetry](https://python-poetry.org/docs/#installation)
- `git clone` this repo
- If you already have a Spansh `galaxy_populated.json` data dump, add it to `data/` with default filename
  - If so, `make import-spansh` instead of `make run-pipeline`

### Setup
```
make setup
make run-pipeline
```

---

# Design Overview

## What This Project Is

This project is a **data ingestion, enrichment, analysis, and workflow automation system** for *Elite Dangerous* game data, built with scalability and adaptability in mind.

We collect, process, and expose structured data from external sources like **Spansh**, **EDSM**, and **EDDN**, and allow allowlisted users to interact with insights via:
- CLI tools
- REST APIs
- Automated notifications (e.g., Discord bots, Webhooks)

---

## Key Technologies

| Purpose                         | Technology                   | Why |
|:---------------------------------|:------------------------------|:----|
| Project Management              | Poetry                        | Modern Python packaging and dependency management |
| Build Automation                | Makefiles                     | Human-readable, cross-platform dev commands |
| Core Data Modeling              | Pydantic                      | Type-safe schemas, OpenAPI generation, easy codegen |
| CLI Development                 | Typer                         | Pydantic-integrated CLI with minimal boilerplate |
| API Server                      | FastAPI                       | Modern async Python HTTP API, OpenAPI integration |
| Database                        | Postgres + SQLAlchemy         | Relational storage, robust ORM mapping |
| Migrations                      | Alembic                       | Database schema evolution |
| Code Generation (planned)       | OpenAPI, JSON Schema export   | External data contracts and client generation |

---

# Models and Schemas

We organize our data definitions into three major categories (Exact locations subject to change):

## Logical Schemas
- Location: `src/core/models/`
- Purpose: Represent pure domain concepts, independent of technology
- Characteristics:
  - Pydantic models
  - Clean, type-safe, business-focused

## Physical Schemas
- Location: `src/adapters/persistence/postgres/` and `src/alembic/`
- Purpose: Represent how data is stored in persistent systems (e.g., Postgres tables)
- Characteristics:
  - SQLAlchemy models
  - Manual migrations with Alembic

## External Schemas
- Location: `gen/`, `src/ingestion/spansh/models/`
- Purpose: Represent third-party schema definitions (e.g., EDDN event formats)
- Characteristics:
  - Pydantic models, some auto-generated from external JSON Schemas
  - Used for ingesting external messages safely
