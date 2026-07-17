.PHONY: help install install-dev lint format test coverage clean

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
	pip install -e sdk/
	pip install -r requirements.txt

install-dev:
	make install
	pip install -r requirements-dev.txt
	pre-commit install

lint:
	flake8 sdk/ orchestrator/ capture/ reconstruction/ semantic/ robot/ sarvam/ tests/
	mypy sdk/ orchestrator/ capture/ reconstruction/ semantic/ robot/ sarvam/ tests/

format:
	black sdk/ orchestrator/ capture/ reconstruction/ semantic/ robot/ sarvam/ tests/
	isort sdk/ orchestrator/ capture/ reconstruction/ semantic/ robot/ sarvam/ tests/

test:
	pytest

coverage:
	pytest --cov-report=term-missing --cov-report=html

clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/ htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
