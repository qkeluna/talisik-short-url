# Talisik Short URL

A privacy-focused URL shortener designed as both a reusable library and standalone web service. Built with Kaizen principles for sustainable, incremental development.

## Architecture

- **Core Library** (`talisik/`): Pure Python library for URL shortening logic
- **API Service** (`api/`): FastAPI-based REST service
- **Web UI** (`web/`): React + ShadCN + TypeScript frontend
- **CLI Tool** (`cli/`): Command-line interface

## Features

- 🔒 Privacy-first design (inspired by tnyr.me)
- 📦 Importable as Python library
- 🌐 Web interface for end users
- 🛠️ REST API for integrations
- ⚡ Modern tech stack with excellent DX

## Quick Start

```bash
# Install core library
pip install -e .

# Start API service
cd api && uvicorn main:app --reload

# Start web UI
cd web && npm run dev
```

## Documentation

📚 **Comprehensive Documentation**: See the [`docs/`](docs/) folder for detailed information:

- 📋 [Product Requirements](docs/product_requirement_docs.md) - Project goals, requirements, and roadmap
- 🏗️ [Architecture](docs/architecture.md) - System design and component relationships
- 🔧 [Technical](docs/technical.md) - Development environment and implementation details
- 📊 [Workflow Diagrams](docs/workflow-diagram.md) - Visual representations of how the system works

## Development Status

- [x] Project structure
- [x] Core library implementation ✅
- [x] Basic shortening algorithm ✅
- [x] Storage abstraction (in-memory) ✅
- [ ] Multiple storage backends
- [ ] REST API endpoints
- [ ] Web frontend
- [ ] CLI interface

## Tech Stack

**Backend**: Python 3.9+, FastAPI, Pydantic
**Frontend**: React, TypeScript, Vite, ShadCN/UI
**Testing**: pytest, Vitest
**DevOps**: Docker, GitHub Actions
