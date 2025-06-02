# Talisik Short URL - Development Commands

.PHONY: venv install test lint format clean dev help api test-api

# Create virtual environment
venv:
	python3 -m venv venv
	@echo "✅ Virtual environment created!"
	@echo "Run 'source venv/bin/activate' to activate it"

# Install the package in development mode (assumes venv is activated)
install:
	pip install -e ".[dev]"
	pip install requests

# Install everything from scratch (creates venv + installs)
setup: venv
	source venv/bin/activate && pip install -e ".[dev]" && pip install requests
	@echo "✅ Complete setup finished!"
	@echo "Run 'source venv/bin/activate' to activate your environment"

# Run tests with coverage
test:
	pytest -v

# Run API server
api:
	cd api && uvicorn main:app --reload --port 8000

# Test API endpoints
test-api:
	python test_api.py

# Run linting
lint:
	ruff check talisik/ tests/ api/
	black --check talisik/ tests/ api/

# Format code
format:
	black talisik/ tests/ api/
	ruff --fix talisik/ tests/ api/

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -delete

# Clean everything including venv
clean-all: clean
	rm -rf venv/

# Start development - assumes venv is activated
dev: install test
	@echo "✅ Development environment ready!"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make api' to start the API server"
	@echo "Run 'python -c \"from talisik import URLShortener; print('Library imported successfully!')\"' to test import"

# Show help
help:
	@echo "Talisik Short URL - Development Commands"
	@echo ""
	@echo "First time setup:"
	@echo "  make setup          - Create venv and install everything"
	@echo ""
	@echo "Daily development (with activated venv):"
	@echo "  source venv/bin/activate  - Activate virtual environment"
	@echo "  make dev            - Install deps and run tests"
	@echo "  make test           - Run unit tests with coverage"
	@echo "  make api            - Start FastAPI server on port 8000"
	@echo "  make test-api       - Test API endpoints"
	@echo "  make lint           - Check code quality"
	@echo "  make format         - Format code"
	@echo ""
	@echo "Interactive testing:"
	@echo "  python cli_demo.py  - Interactive CLI demo"
	@echo "  python test_demo.py - Automated library demo"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove build artifacts"
	@echo "  make clean-all      - Remove everything including venv" 