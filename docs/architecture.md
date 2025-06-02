# Talisik Short URL - System Architecture

## Overview

Talisik Short URL follows a modular, library-first architecture designed for maximum flexibility and maintainability. The system is built around a core library that can be used standalone or extended with various interfaces (API, Web, CLI).

> 📊 **Visual Workflows**: For detailed visual representations of how the URL shortener works, including flowcharts and sequence diagrams, see [Workflow Diagrams](workflow-diagram.md).

## Architectural Principles

### 1. Library-First Design

- **Core functionality** is implemented as a pure Python library
- **No external dependencies** for basic operations (library mode)
- **Clean API** for embedding in other applications
- **Pluggable backends** for different storage needs

### 2. Separation of Concerns

- **Core Logic**: URL shortening and expansion algorithms
- **Data Models**: Type-safe data structures using dataclasses
- **Storage Layer**: Abstracted persistence with multiple implementations
- **Interface Layer**: APIs, Web UI, and CLI as separate concerns

### 3. Kaizen Development Philosophy

- **Incremental complexity**: Start simple, add features progressively
- **Test-driven**: Each component has comprehensive test coverage
- **Refactoring-friendly**: Clean code that's easy to modify
- **Documentation-first**: Every component is well-documented

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Interface Layer                          │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Web UI        │   REST API      │      CLI Tool           │
│  (React/TS)     │   (FastAPI)     │     (Click/Typer)       │
└─────────────────┴─────────────────┴─────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                   Core Library                              │
├─────────────────────────────────────────────────────────────┤
│                 URLShortener                                │
│           (Main Business Logic)                             │
├─────────────────────────────────────────────────────────────┤
│     Models         │      Storage Interface                 │
│  - ShortURL        │   - AbstractStorage                    │
│  - ShortenRequest  │   - get/set/delete                     │
│  - ShortenResponse │   - list/expire                        │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                Storage Implementations                      │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Memory        │     SQLite      │        Redis            │
│  (Current)      │    (Planned)    │      (Planned)          │
│                 │                 │                         │
│ - In-memory     │ - File-based    │ - Distributed           │
│ - Fast          │ - Persistent    │ - High-performance      │
│ - Non-persistent│ - ACID          │ - TTL support           │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## Component Architecture

### Core Library (`talisik/`)

#### 1. URLShortener Class

**Location**: `talisik/core/shortener.py`

**Responsibilities**:

- Main entry point for URL shortening operations
- Orchestrates validation, code generation, and storage
- Handles business logic for expiration and analytics

**Key Methods**:

```python
def shorten(request: ShortenRequest) -> ShortenResponse
def expand(short_code: str) -> Optional[str]
```

**Design Patterns**:

- **Facade Pattern**: Simplifies complex operations behind a clean interface
- **Strategy Pattern**: Pluggable storage backends (future)
- **Factory Pattern**: Code generation strategies (future)

#### 2. Data Models

**Location**: `talisik/core/models.py`

**Components**:

- `ShortURL`: Core entity representing a shortened URL with metadata
- `ShortenRequest`: Input model for shortening operations
- `ShortenResponse`: Output model with generated URLs and metadata

**Design Decisions**:

- **Dataclasses**: Simple, type-safe, and lightweight
- **Immutable where possible**: Reduces side effects
- **Optional fields**: Support for future features without breaking changes

#### 3. Storage Layer (Current: In-Memory)

**Location**: Currently embedded in `URLShortener`

**Current Implementation**:

```python
self._urls: dict[str, ShortURL] = {}
```

**Future Architecture**:

```python
class AbstractStorage(ABC):
    @abstractmethod
    def get(self, short_code: str) -> Optional[ShortURL]

    @abstractmethod
    def set(self, short_code: str, url: ShortURL) -> None

    @abstractmethod
    def delete(self, short_code: str) -> bool

    @abstractmethod
    def list_expired(self) -> List[str]
```

### Interface Layer (Planned)

#### 1. REST API Service

**Technology**: FastAPI + Uvicorn
**Location**: `api/` (planned)

**Endpoints**:

```
POST /shorten     - Create short URL
GET  /{code}      - Redirect to original URL
GET  /api/{code}  - Get URL metadata
DELETE /api/{code} - Delete short URL
GET  /health      - Health check
```

**Features**:

- OpenAPI/Swagger documentation
- Request validation with Pydantic
- Rate limiting and security headers
- CORS support for web integration

#### 2. Web Interface

**Technology**: React + TypeScript + Vite + ShadCN/UI
**Location**: `web/` (planned)

**Components**:

- URL shortening form
- Results display with copy functionality
- Basic analytics dashboard
- Responsive design for mobile/desktop

#### 3. CLI Tool

**Technology**: Click or Typer
**Location**: `cli/` (planned)

**Commands**:

```bash
talisik shorten <url>
talisik expand <code>
talisik list
talisik config
```

## Data Flow Architecture

### URL Shortening Flow

```
1. User Input → ShortenRequest
2. URLShortener.shorten()
   ├─ Validate URL
   ├─ Generate/validate short code
   ├─ Create ShortURL entity
   ├─ Store in backend
   └─ Return ShortenResponse
3. Response → User Interface
```

### URL Expansion Flow

```
1. Short Code → URLShortener.expand()
2. Storage lookup
3. Expiration check
4. Analytics update
5. Return original URL or None
```

## Storage Architecture

### Current: In-Memory Storage

**Pros**:

- Zero dependencies
- Maximum performance
- Simple implementation
- Perfect for testing and development

**Cons**:

- No persistence across restarts
- Limited by available RAM
- No distributed support

### Planned: SQLite Storage

**Use Cases**:

- Development and small deployments
- File-based persistence needed
- ACID transactions required

**Schema**:

```sql
CREATE TABLE short_urls (
    id TEXT PRIMARY KEY,
    original_url TEXT NOT NULL,
    short_code TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP,
    click_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1
);

CREATE INDEX idx_short_code ON short_urls(short_code);
CREATE INDEX idx_expires_at ON short_urls(expires_at);
```

### Planned: Redis Storage

**Use Cases**:

- High-performance requirements
- Distributed deployments
- Built-in TTL support needed

**Data Structure**:

```
Key: "url:{short_code}"
Value: JSON serialized ShortURL object
TTL: Automatic expiration support
```

## Security Architecture

### Input Validation

- **URL Validation**: Comprehensive parsing and validation
- **Short Code Validation**: Pattern matching and sanitization
- **Request Size Limits**: Prevent abuse through large payloads

### Code Generation Security

- **Cryptographically Secure**: Using `secrets` module
- **Collision Resistant**: 7-character codes = 62^7 ≈ 3.5 trillion combinations
- **No Predictable Patterns**: True random generation

### Privacy Protection

- **Minimal Data Collection**: Only essential metadata stored
- **No User Tracking**: No IP logging or user identification
- **Configurable Analytics**: Optional click counting
- **Data Retention**: Automatic expiration support

### API Security (Planned)

- **Rate Limiting**: Prevent abuse and DoS attacks
- **CORS Configuration**: Controlled cross-origin access
- **Input Sanitization**: Comprehensive request validation
- **Security Headers**: HSTS, CSP, and other protective headers

## Performance Architecture

### Core Library Performance

- **O(1) Operations**: Hash-based lookups for URL expansion
- **Memory Efficient**: Minimal object overhead with dataclasses
- **CPU Optimized**: Efficient algorithms for code generation
- **Thread Safety**: Planned support for concurrent access

### Caching Strategy (Planned)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   L1 Cache  │    │   L2 Cache  │    │  Storage    │
│  (Memory)   │    │   (Redis)   │    │ (SQLite)    │
│             │    │             │    │             │
│ Hot URLs    │ → │ Warm URLs   │ → │ All URLs    │
│ <1ms        │    │ <10ms       │    │ <100ms      │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Scalability Considerations

- **Horizontal Scaling**: Redis backend supports multiple instances
- **Load Balancing**: Stateless design enables easy load distribution
- **Database Sharding**: Short code-based partitioning strategy
- **CDN Integration**: Static assets and redirect caching

## Error Handling Architecture

### Exception Hierarchy

```python
class TalisikError(Exception):
    """Base exception for all Talisik errors"""

class ValidationError(TalisikError):
    """Invalid input provided"""

class StorageError(TalisikError):
    """Storage backend failure"""

class ConflictError(TalisikError):
    """Short code already exists"""
```

### Error Recovery Strategies

- **Graceful Degradation**: Continue operation with reduced functionality
- **Retry Logic**: Automatic retry for transient failures
- **Circuit Breaker**: Prevent cascade failures in distributed setup
- **Fallback Mechanisms**: Alternative code generation on conflicts

## Testing Architecture

### Test Structure

```
tests/
├── unit/                 # Unit tests for individual components
│   ├── test_shortener.py # Core functionality tests
│   ├── test_models.py    # Data model tests
│   └── test_storage.py   # Storage backend tests
├── integration/          # Integration tests
│   ├── test_api.py       # API endpoint tests
│   └── test_e2e.py       # End-to-end scenarios
└── performance/          # Performance and load tests
    ├── test_load.py      # Load testing
    └── test_bench.py     # Benchmarking
```

### Test Coverage Strategy

- **Unit Tests**: >95% coverage for core library
- **Integration Tests**: All API endpoints and workflows
- **Property-Based Testing**: Edge cases and input validation
- **Performance Tests**: Latency and throughput benchmarks

## Configuration Architecture

### Library Configuration

```python
@dataclass
class TalisikConfig:
    base_url: str = "http://localhost:3000"
    default_code_length: int = 7
    max_custom_code_length: int = 50
    storage_backend: str = "memory"
    enable_analytics: bool = True
```

### Environment-Based Configuration

```python
# Development
TALISIK_BASE_URL=http://localhost:3000
TALISIK_STORAGE=memory

# Production
TALISIK_BASE_URL=https://short.example.com
TALISIK_STORAGE=redis://redis:6379/0
```

## Deployment Architecture

### Development Deployment

- **Local Development**: In-memory storage, FastAPI dev server
- **Testing**: SQLite storage, pytest with coverage
- **Docker Compose**: Multi-service development environment

### Production Deployment

```yaml
# docker-compose.yml
services:
  api:
    image: talisik/api:latest
    environment:
      - TALISIK_STORAGE=redis://redis:6379/0

  web:
    image: talisik/web:latest
    environment:
      - API_URL=http://api:8000

  redis:
    image: redis:alpine
    volumes:
      - redis_data:/data
```

### Cloud Deployment Options

- **Container Platforms**: Docker, Kubernetes, Cloud Run
- **Serverless**: AWS Lambda, Vercel Functions (for API)
- **Static Hosting**: Netlify, Vercel (for Web UI)
- **Database**: Managed Redis, RDS, or embedded SQLite

## Monitoring and Observability

### Metrics Collection (Planned)

- **Performance Metrics**: Response times, throughput, error rates
- **Business Metrics**: URLs created, clicks, popular domains
- **System Metrics**: Memory usage, storage size, cache hit rates

### Logging Strategy

- **Structured Logging**: JSON format for easy parsing
- **Log Levels**: DEBUG, INFO, WARN, ERROR with appropriate usage
- **Privacy**: No sensitive data in logs (URLs, user info)
- **Retention**: Configurable log retention policies

### Health Checks

```python
GET /health
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "0.1.0",
    "storage": {
        "type": "redis",
        "status": "connected",
        "latency_ms": 2.3
    }
}
```

## Future Architecture Considerations

### Microservices Evolution

- **URL Service**: Core shortening functionality
- **Analytics Service**: Click tracking and reporting
- **Admin Service**: Management and configuration
- **Notification Service**: Alerts and monitoring

### API Gateway Integration

- **Rate Limiting**: Centralized rate limiting policies
- **Authentication**: OAuth2/JWT integration
- **Load Balancing**: Intelligent request routing
- **Caching**: Response caching at gateway level

### Event-Driven Architecture

```
URL Created → Analytics Event → Metrics Update
URL Clicked → Analytics Event → Dashboard Update
URL Expired → Cleanup Event → Storage Cleanup
```

This architecture provides a solid foundation for the current implementation while enabling smooth evolution toward more complex deployments and features as the project grows following Kaizen principles.
