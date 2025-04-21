.PHONY: install lint type

install:
	poetry install

lint:
	black --check .
	isort --check-only .
	flake8 .

lintfix:
	black .
	isort .

type:
	mypy src

check: lint type
