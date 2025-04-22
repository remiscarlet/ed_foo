.PHONY: install lint lintfix type check lintfixcheck

install:
	poetry install

lint:
	poetry run black --check .
	poetry run isort --check-only .
	poetry run flake8 . -v

lintfix:
	poetry run black .
	poetry run isort .

type:
	poetry run mypy .

check: lint type

lintfixcheck:
	poetry run black .
	poetry run isort .
	poetry run flake8 . -v
	poetry run mypy .