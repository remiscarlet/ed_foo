## ED Foo Or Something
<sub>...Enhanced Knowledge Analysis and Insights Notification Engine</sub>

Extremely WIP refactor.

# Design

## What
- Poetry for project/package management
    - Makefiles for build workflows
- Uses Hexagonal/Ports and Adapters Code Architecture
- Pydantic Types
    - Core pydantic models will be used as the source of truth for codegen as well
    - Typer for pydantic-integrated CLI args
- FastAPI for HTTP
- Codegen for schemas
    - JSON Schemas for EDDN
    - OpenAPI defs

## Why Hexagonal/Ports and Adapters Architecture
We have some core logical functionality we want to expose - data analysis and reports about them. The exact source of data and where or how the data is presented is not a primary concern.

Our data can come from multiple source like Spansh, EDSM, or EDDN. All have different formats, meaning we need our own internal format for consistency. People might use the analysis results through CLI commands, use a REST API/WebUI, rely on Discord webhook events through Crons, or other methods. This all means the "inputs" and "outputs" are numerous and we want to avoid any tight coupling of technology or interface choices.

The Hexagonal architecture lends itself well to these design concerns and thus was chosen.

## Models and Schemas
We have three major categories of models and schemas:
  - "Logical" Schemas
  - "Physical" Schemas
  - "External" Schemas

### Logical Schemas
 "Logical" schemas are the ones we interact with the most in the code. It represents the purest conceptual shapes we work with, with a focus on usability and ergonomics as the primary concerns.

- `src/core/models/`
- Represents how we work with data
- Not tied to any specific framework or technology - it's tech agnostic and domain-specific to our core business logic.

### Physical Schemas
"Physical" schemas are how we physically store the data. This is technology-dependent, such as storing data in Postgres.

- `src/adapters/persistence/postgres/`
- `src/alembic/`
- Represents implementation details of how we store the data
- Requires mapping Logical schemas to Physical schemas
  - Boilerplate-y, but cost of logical abstractions/Ports and Adapters architecture
- Manually written migrations
  - Ideally run as part of CICD

### External Schemas
Schemas defined by third parties that we may want to use in Python code.

- `gen/`
- Currently only `gen/eddn_models/`
  - Generated from their JSON Schemas

# Developing

## Makefile
- Setup
  - `make install`
- Lint + fix, type check
  - `make lintfixcheck`
- Generate EDDN pydantic models
  - `make models`


# Future TODOs
- CICD once there's a bit more clarity on existing infra and resources
- Consider a command bus pattern once we have a non-trivial number of "commands"/"workflows"
