.PHONY: install download-spansh lint lint-fix type check lint-fix-check download-eddn-models gen-eddn-models models

## Setup

install:
	poetry install

## Data DL/Import

download-spansh:
	poetry run cli data download-spansh-dump

## Code Quality

lint:
	poetry run yamllint **/*.yaml
	poetry run lint_metadata
	poetry run black --check .
	poetry run isort --check-only .
	poetry run flake8 . -v

lint-fix:
	poetry run yamlfix **/*.yaml
	poetry run lint_metadata
	poetry run black .
	poetry run isort .

type:
	poetry run mypy src/

check: lint type

lint-fix-check:
	poetry run yamlfix **/*.yaml
	poetry run lint_metadata
	poetry run black .
	poetry run isort .
	poetry run flake8 . -v
	poetry run mypy src/

## Docker (Dev Only)

pg-shell: # "Lightweight" PG shell for convenience
	poetry run pgcli "postgres://e_kaine:e_kaine_pw@localhost:5432/e_kaine"

nuke-db:
	docker stop ekaine_db
	docker rm ekaine_db

up:
	docker compose -f tools/docker/docker-compose.yaml up --build

down:
	docker compose -f tools/docker/docker-compose.yaml down

up-db:
	docker compose -f tools/docker/docker-compose.yaml up --build -d db

down-db:
	docker compose -f tools/docker/docker-compose.yaml stop db

## Alembic

alembic-upgrade:
	poetry run alembic upgrade head

alembic-revision:
	poetry run alembic revision --autogenerate

## Code Gen


download-eddn-models:
	mkdir data
	git clone https://github.com/EDCD/EDDN.git data/eddn/ 2>/dev/null || true
	git -C data/eddn pull

gen-eddn-models: download-eddn-models
	mkdir -p data/_tmp
	cp data/eddn/schemas/*.json data/_tmp
	mkdir gen
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


# make nuke-db; make up-db; sleep 1; rm -rf src/alembic/versions/*; make alembic-revision; make alembic-upgrade;