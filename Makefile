.PHONY: bootstrap check test test-integration test-e2e build prepare-release release-check-local release-check

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

prepare-release:
	npm run build
	python infrastructure/scripts/build_release_manifest.py

release-check-local: prepare-release
	python infrastructure/scripts/verify_release.py

release-check: prepare-release
	python infrastructure/scripts/verify_release.py --containers
