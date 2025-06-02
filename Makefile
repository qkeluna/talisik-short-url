# Talisik Short URL - Development Commands

.PHONY: venv install test lint format clean dev help api test-api demo-js

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
	@echo "Talisik Short URL - Available Commands:"
	@echo ""
	@echo "  make venv           - Create virtual environment"
	@echo "  make install        - Install dependencies" 
	@echo "  make test           - Run tests"
	@echo "  make test-coverage  - Run tests with coverage report"
	@echo "  make lint           - Run code linting"
	@echo "  make format         - Format code"
	@echo "  make dev            - Start development environment"
	@echo "  make api            - Start API server"
	@echo "  make test-api       - Test API endpoints"
	@echo "  make demo-js        - Run JavaScript/React integration demo"
	@echo "  make clean          - Remove build artifacts"
	@echo "  make clean-all      - Remove everything including venv"

# Run JavaScript/React integration demo
demo-js:
	@echo "Running JavaScript integration demo..."
	@echo "Make sure API is running: make api"
	node examples/react_demo.js 