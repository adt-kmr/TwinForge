.PHONY: help install install-dev lint format test coverage clean build dist release security check-all

help:
	@echo "Usage:"
	@echo "  make install       Install production dependencies"
	@echo "  make install-dev   Install development dependencies"
	@echo "  make lint          Run linters (flake8, mypy)"
	@echo "  make format        Format code (black, isort)"
	@echo "  make test          Run tests with pytest"
	@echo "  make coverage      Run tests with coverage report"
	@echo "  make clean         Clean build artifacts"
	@echo "  make build         Build source and wheel distributions"
	@echo "  make security      Run security checks (bandit, safety)"
	@echo "  make check-all     Run all checks (format, lint, test, security)"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

lint:
	flake8 src/ tests/
	mypy src/ tests/

format:
	black src/ tests/
	isort src/ tests/

test:
	pytest

coverage:
	pytest --cov=src --cov-report=term-missing --cov-report=html

clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf htmlcov/ coverage/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

security:
	bandit -r src/ -ll
	safety check

check-all: format lint test security
	@echo "All checks passed!"
