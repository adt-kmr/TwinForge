# Contributing to TwinForge

We love your input! We want to make contributing as easy and transparent as possible.

## Development Process

1. Fork the repo and create your branch from `main`
2. If you've added code, add tests
3. Ensure the test suite passes
4. Make sure your code passes linting
5. Issue a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/twinforge/twinforge.git
cd twinforge

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
make install-dev

# Install pre-commit hooks
pre-commit install
```

## Code Style

- We use [Black](https://github.com/psf/black) with line length 100
- We use [isort](https://github.com/PyCQA/isort) with Black profile
- We use [flake8](https://github.com/PyCQA/flake8) for linting
- We use [mypy](https://github.com/python/mypy) for type checking

## Testing

- All tests should pass before submitting a PR
- New features should include tests
- Run tests: `make test`
- Check coverage: `make coverage`

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the CHANGELOG.md
3. The PR will be merged once you have sign-off from maintainers

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.
