.PHONY: help sync test clean-build build publish publish-test

help:
	@echo "Targets:"
	@echo "  make sync         Install/update dependencies"
	@echo "  make test         Run test suite"
	@echo "  make clean-build  Remove build artifacts (dist, dist.*, build, *.egg-info)"
	@echo "  make build        Clean and build package"
	@echo "  make publish      Build and publish to PyPI (uses PYPI_TOKEN from env)"
	@echo "  make publish-test Build and publish to TestPyPI (uses TEST_PYPI_TOKEN from env)"

sync:
	uv sync

test:
	uv run pytest

clean-build:
	rm -rf dist build
	find . -maxdepth 1 -type d -name 'dist.*' -exec rm -rf {} +
	find . -maxdepth 1 -type d -name '*.egg-info' -exec rm -rf {} +

build: clean-build
	uv build

publish: build
	: "$${PYPI_TOKEN:?PYPI_TOKEN is required}"
	uv publish --token "$${PYPI_TOKEN}"

publish-test: build
	: "$${TEST_PYPI_TOKEN:?TEST_PYPI_TOKEN is required}"
	uv publish --publish-url https://test.pypi.org/legacy/ --token "$${TEST_PYPI_TOKEN}"
