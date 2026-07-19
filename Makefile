.PHONY: help install install-dev lint format format-check test coverage clean

# Every source tree we lint/format/typecheck. CI reuses these targets, so this
# list is the single place to add a new stage package.
PKGS = sdk/ orchestrator/ capture/ reconstruction/ semantic/ robot/ sarvam/ twin/ policy/ deployment/ tests/

help:
	@echo "Usage:"
	@echo "  make install       Install SDK + dependencies"
	@echo "  make install-dev   Install dev dependencies + pre-commit"
	@echo "  make lint          Run flake8 + mypy"
	@echo "  make format        Run black + isort"
	@echo "  make test          Run pytest"
	@echo "  make coverage      Run pytest with coverage"
	@echo "  make clean         Remove build artifacts"

install:
	pip install -e .
	pip install -r requirements.txt

install-dev:
	make install
	pip install -r requirements-dev.txt
	pre-commit install

lint:
	flake8 $(PKGS)
	mypy $(PKGS)

format:
	black $(PKGS)
	isort $(PKGS)

format-check:
	black --check $(PKGS)
	isort --check-only $(PKGS)

test:
	pytest

coverage:
	pytest --cov-report=term-missing --cov-report=html

clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/ htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
