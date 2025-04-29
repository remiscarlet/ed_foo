.PHONY: install lint lintfix type check lintfixcheck download_eddn_models gen_eddn_models models

## Setup

install:
	poetry install

## Code Quality

lint:
	poetry run yamllint **/*.yaml
	poetry run lint_metadata
	poetry run black --check .
	poetry run isort --check-only .
	poetry run flake8 . -v

lintfix:
	poetry run yamlfix **/*.yaml
	poetry run lint_metadata
	poetry run black .
	poetry run isort .

type:
	poetry run mypy src/

check: lint type

lintfixcheck:
	poetry run yamlfix **/*.yaml
	poetry run lint_metadata
	poetry run black .
	poetry run isort .
	poetry run flake8 . -v
	poetry run mypy src/

## Docker (Dev Only)

up:
	docker compose -f tools/docker/docker-compose.yaml up --build

down:
	docker compose -f tools/docker/docker-compose.yaml down

updb:
	docker compose -f tools/docker/docker-compose.yaml up --build -d db

downdb:
	docker compose -f tools/docker/docker-compose.yaml stop db


## Code Gen


download_eddn_models:
	mkdir data
	git clone https://github.com/EDCD/EDDN.git data/eddn/ 2>/dev/null || true
	git -C data/eddn pull

gen_eddn_models: download_eddn_models
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
models: gen_eddn_models