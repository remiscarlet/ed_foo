.PHONY: install setup download-spansh import-spansh run-pipeline lint lint-fix type check lint-fix-check download-eddn-models gen-eddn-models models

## Setup

install:
	poetry install

setup: install up alembic-upgrade install-eddn-models

## Data DL/Import

download-spansh:
	poetry run cli ingestion download-spansh

import-spansh:
	poetry run cli ingestion import-spansh

import-spansh-v:
	poetry run cli ingestion import-spansh -v

import-spansh-vv:
	poetry run cli ingestion import-spansh -vv

run-pipeline: download-spansh import-spansh-v

## Code Quality

lint:
	poetry run yamllint **/*.yaml
	poetry run lint_metadata
	poetry run black --check src/
	poetry run isort --check-only src/
	poetry run flake8 src/ -v
	poetry run sqlfluff lint --dialect postgres .

lint-fix:
	poetry run yamlfix **/*.yaml
	poetry run lint_metadata
	poetry run black src/
	poetry run isort src/
	poetry run sqlfluff fix --dialect postgres .

type:
	poetry run mypy src/

check: lint type

lint-fix-check:
	poetry run yamlfix **/*.yaml
	poetry run lint_metadata
	poetry run black src/
	poetry run isort src/
	poetry run flake8 src/ -v
	poetry run mypy src/
	poetry run sqlfluff fix --dialect postgres .

## Docker (Dev Only)

pg-shell: # "Lightweight" PG shell for convenience
	poetry run pgcli "postgres://e_kaine:e_kaine_pw@localhost:5432/e_kaine"

nuke-db:
	docker stop ekaine_db
	docker rm ekaine_db

up:
	docker compose -f tools/docker/docker-compose.yaml up --build -d

down:
	docker compose -f tools/docker/docker-compose.yaml down

up-db:
	docker compose -f tools/docker/docker-compose.yaml up --build -d postgres

down-db:
	docker compose -f tools/docker/docker-compose.yaml stop postgres

## Alembic

alembic-downgrade-one:
	poetry run alembic downgrade -1

alembic-upgrade:
	poetry run alembic upgrade head

alembic-revision:
	poetry run alembic revision --autogenerate

## Code Gen

download-eddn-models:
	mkdir -p data
	git clone https://github.com/EDCD/EDDN.git data/eddn/ 2>/dev/null || true
	git -C data/eddn pull

gen-eddn-models: download-eddn-models
	mkdir -p data/_tmp
	cp data/eddn/schemas/*.json data/_tmp
	mkdir -p gen
	poetry run datamodel-codegen \
		--reuse-model \
		--strict-nullable \
		--input-file-type jsonschema \
		--input data/_tmp \
		--output-model-type pydantic_v2.BaseModel \
		--output gen/eddn_models/
	touch gen/__init__.py
	touch gen/eddn_models/__init__.py
models: gen-eddn-models

install-eddn-models: download-eddn-models gen-eddn-models

# make nuke-db; make up-db; sleep 1; make alembic-upgrade; make alembic-revision; make alembic-upgrade;