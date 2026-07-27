.PHONY: bootstrap check test test-integration test-e2e build release-check

bootstrap:
	python -m pip install -e ".[dev]"
	npm install

check:
	python -m ruff check .
	python -m ruff format --check .
	python -m mypy
	npm run lint
	npm run typecheck

test:
	python -m pytest
	npm test

test-integration:
	python -m pytest -m integration

test-e2e:
	npm --workspace ui run test:e2e

build:
	npm run build
	python -m build

release-check:
	python infrastructure/scripts/verify_release.py --containers
