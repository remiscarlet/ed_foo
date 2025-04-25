# ED Foo (Enhanced Knowledge Analysis and Insights Notification Engine)

<sub>Extremely WIP — initial refactor in progress.</sub>

---

# Design Overview

## What This Project Is

This project is a **data ingestion, enrichment, analysis, and workflow automation system** for *Elite Dangerous* game data, built with scalability and adaptability in mind.

We collect, process, and expose structured data from external sources like **Spansh**, **EDSM**, and **EDDN**, and allow internal and external users to interact with insights via:
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

# Code Architecture

## Why Hexagonal (Ports and Adapters) Architecture?

The system must be flexible about:
- **Where data comes from** (e.g., EDSM dumps, live EDDN feeds, manually entered data)
- **Where results go** (e.g., CLI display, API endpoints, webhook events)

Thus, we separate **core domain logic** from **input/output concerns**.
This avoids coupling the system tightly to any specific data source or delivery mechanism.

| Layer | Responsibility |
|:------|:---------------|
| Core (Domain) | Pure business logic, technology-agnostic |
| Ports (Interfaces) | Abstract contract definitions (e.g., User storage) |
| Adapters | Technology-specific implementations (e.g., SQLAlchemy, FastAPI) |

This structure allows:
- Adding new ingestion sources easily
- Exposing workflows through new channels (CLI, API, Discord) with minimal duplication
- Isolating tests cleanly at each layer

---

# Models and Schemas

We organize our data definitions into three major categories:

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
  - Mappings between Logical and Physical schemas as needed

> **Note**: This introduces some unavoidable boilerplate but pays off in flexibility and clarity.

## External Schemas
- Location: `gen/`
- Purpose: Represent third-party schema definitions (e.g., EDDN event formats)
- Characteristics:
  - Pydantic models auto-generated from external JSON Schemas
  - Used for ingesting external messages safely

---

# Development

## Key Makefile Commands

| Command | Purpose |
|:--------|:--------|
| `make install` | Set up Python environment |
| `make lintfixcheck` | Lint, auto-fix, and type-check |
| `make export-schema` | Generate and save JSON Schemas from Pydantic models |
| `make run-api` | Run local FastAPI server via Uvicorn |
| `make cli` | Run CLI entrypoint |
| `make migrate` | Create new Alembic migration |
| `make upgrade` | Apply Alembic migrations |

---

# Future TODOs

- Set up full **CI/CD pipeline** (likely GitHub Actions)
- Introduce optional **Command Bus** pattern for CLI and API workflow invocation
- Explore async ORM integration (SQLAlchemy 2.0 async support)
- Expand ingestion sources beyond EDSM/EDDN
- Add in-memory and background workers (for task queues, webhook triggers)
- Add basic operational monitoring (metrics, logging)

---

# Design Philosophy

This system is engineered for **durability**, **extensibility**, and **clean separation of concerns**.
We favor slightly more boilerplate up-front to achieve long-term adaptability as project complexity grows.

> *Tech debt is managed by modularity, not shortcuts.*

---

# Quickstart Example

```bash
# Install deps
make install

# Run Docker-based dev server
make up
make down
```

---

# Closing Notes

This project is designed with the assumption that it will grow significantly in scope and complexity over time.
Architecture choices prioritize **clarity, extensibility, and ergonomics for future developers** — even at some cost to initial verbosity.

