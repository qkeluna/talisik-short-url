# Talisik Short URL - Technical Documentation

## Development Environment

### Prerequisites

- **Python**: 3.9+ (tested with 3.9, 3.10, 3.11)
- **Package Manager**: pip (with virtual environment recommended)
- **Operating System**: macOS, Linux, Windows (WSL recommended)
- **Memory**: Minimum 512MB available RAM
- **Storage**: 100MB for development environment

### Environment Setup

#### Quick Setup

```bash
# Clone repository
git clone <repository-url>
cd talisik-short-url

# Create and activate virtual environment
make setup

# Activate environment (run this each time)
source venv/bin/activate

# Verify installation
python -c "from talisik import URLShortener; print('✅ Installation successful')"
```

#### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests to verify
pytest
```

### Development Workflow

```bash
# Daily development cycle
source venv/bin/activate    # Activate environment
make dev                   # Install deps + run tests
make test                  # Run test suite
make lint                  # Check code quality
make format                # Format code
```

## Technology Stack

### Core Technologies

#### Language and Runtime

- **Python 3.9+**: Modern Python with type hints and dataclasses
- **Type Checking**: Built-in `typing` module with strict type hints
- **Standard Library**: Leverages `secrets`, `datetime`, `urllib.parse`

#### Dependencies (Core Library)

```python
# Required dependencies
pydantic>=2.0.0  # Data validation and serialization

# Development dependencies
pytest>=7.0.0         # Testing framework
pytest-cov>=4.0.0     # Coverage reporting
black>=23.0.0          # Code formatting
ruff>=0.1.0           # Fast Python linter
```

#### Future Stack (Planned)

```python
# API Service
fastapi>=0.100.0       # Modern web framework
uvicorn[standard]>=0.20.0  # ASGI server

# Storage Backends
aiosqlite>=0.19.0      # Async SQLite
redis>=4.5.0           # Redis client

# CLI Tool
click>=8.0.0           # Command-line interface
rich>=13.0.0           # Beautiful terminal output
```

### Architecture Decisions

#### 1. Library-First Approach

**Decision**: Build core functionality as an importable library first
**Rationale**:

- Maximum reusability across different interfaces
- Easier testing and debugging
- Lower coupling between components
- Supports embedded use cases

**Implementation**:

```python
# Clean importable API
from talisik import URLShortener, ShortenRequest

shortener = URLShortener()
result = shortener.shorten(ShortenRequest(url="https://example.com"))
```

#### 2. Dataclasses for Models

**Decision**: Use Python dataclasses instead of Pydantic models for core library
**Rationale**:

- Zero external dependencies for core functionality
- Type safety with minimal overhead
- Simple serialization/deserialization
- Excellent IDE support

**Implementation**:

```python
@dataclass
class ShortURL:
    id: str
    original_url: str
    short_code: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    click_count: int = 0
    is_active: bool = True
```

#### 3. In-Memory Storage for MVP

**Decision**: Start with in-memory storage, plan for pluggable backends
**Rationale**:

- Simplest possible implementation
- Zero external dependencies
- Perfect for development and testing
- Easy to replace with persistent storage later

**Current Implementation**:

```python
class URLShortener:
    def __init__(self):
        self._urls: dict[str, ShortURL] = {}
```

**Future Abstraction**:

```python
class AbstractStorage(ABC):
    @abstractmethod
    def get(self, short_code: str) -> Optional[ShortURL]: ...

    @abstractmethod
    def set(self, short_code: str, url: ShortURL) -> None: ...
```

#### 4. Cryptographically Secure Code Generation

**Decision**: Use `secrets` module for short code generation
**Rationale**:

- Cryptographically secure randomness
- No predictable patterns
- Collision resistant with 7-character codes (62^7 combinations)

**Implementation**:

```python
def _generate_code(self, length: int = 7) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
```

## Design Patterns

### 1. Facade Pattern

**Location**: `URLShortener` class
**Purpose**: Provides a simplified interface to the complex URL shortening subsystem

```python
class URLShortener:
    """Facade that orchestrates validation, generation, and storage"""

    def shorten(self, request: ShortenRequest) -> ShortenResponse:
        # Orchestrates multiple subsystems
        self._is_valid_url(request.url)      # Validation subsystem
        short_code = self._generate_code()    # Generation subsystem
        self._urls[short_code] = short_url   # Storage subsystem
        return response
```

### 2. Strategy Pattern (Planned)

**Purpose**: Pluggable storage backends without changing core logic

```python
class URLShortener:
    def __init__(self, storage: AbstractStorage = None):
        self.storage = storage or MemoryStorage()

    def shorten(self, request: ShortenRequest) -> ShortenResponse:
        # Uses strategy pattern for storage
        self.storage.set(short_code, short_url)
```

### 3. Factory Pattern (Planned)

**Purpose**: Create different types of storage backends

```python
class StorageFactory:
    @staticmethod
    def create(backend_type: str, **kwargs) -> AbstractStorage:
        if backend_type == "memory":
            return MemoryStorage()
        elif backend_type == "sqlite":
            return SQLiteStorage(kwargs.get('db_path'))
        elif backend_type == "redis":
            return RedisStorage(kwargs.get('redis_url'))
```

### 4. Repository Pattern (Planned)

**Purpose**: Abstraction over data access layer

```python
class URLRepository:
    def __init__(self, storage: AbstractStorage):
        self.storage = storage

    def save(self, short_url: ShortURL) -> None:
        self.storage.set(short_url.short_code, short_url)

    def find_by_code(self, code: str) -> Optional[ShortURL]:
        return self.storage.get(code)
```

## Code Quality Standards

### Code Formatting

**Tool**: Black (line length: 88 characters)

```python
# .pyproject.toml configuration
[tool.black]
line-length = 88
target-version = ['py39']
```

**Example Output**:

```python
def shorten(
    self, request: ShortenRequest
) -> ShortenResponse:  # Automatically formatted
    """Shorten a URL with proper formatting"""
    pass
```

### Linting Rules

**Tool**: Ruff (fast Python linter)

```python
# .pyproject.toml configuration
[tool.ruff]
line-length = 88
target-version = "py39"
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "W",   # pycodestyle warnings
    "UP"   # pyupgrade
]
```

### Type Checking

**Approach**: Comprehensive type hints with strict checking

```python
from typing import Optional, Dict
from datetime import datetime

def expand(self, short_code: str) -> Optional[str]:
    """Type hints ensure API contract clarity"""
    if short_code not in self._urls:
        return None
    return self._urls[short_code].original_url
```

### Documentation Standards

**Docstring Style**: Google-style docstrings

```python
def shorten(self, request: ShortenRequest) -> ShortenResponse:
    """
    Shorten a URL with optional customization.

    Args:
        request: The shortening request containing URL and options

    Returns:
        Response with the shortened URL and metadata

    Raises:
        ValueError: If URL is invalid or short code conflicts

    Example:
        >>> shortener = URLShortener()
        >>> req = ShortenRequest(url="https://example.com")
        >>> resp = shortener.shorten(req)
        >>> print(resp.short_url)
        http://localhost:3000/abc123
    """
```

## Testing Strategy

### Test Framework

**Primary**: pytest with coverage reporting

```python
# pytest configuration in pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=talisik --cov-report=term-missing --cov-report=html"
```

### Test Structure

```
tests/
├── unit/                    # Fast, isolated tests
│   ├── test_shortener.py   # Core functionality
│   ├── test_models.py      # Data models
│   └── test_validation.py  # Input validation
├── integration/            # Component interaction tests
│   ├── test_storage.py     # Storage backends
│   └── test_e2e.py        # End-to-end scenarios
└── performance/           # Performance benchmarks
    └── test_benchmarks.py
```

### Test Categories

#### Unit Tests

**Focus**: Individual functions and methods in isolation

```python
class TestURLShortener:
    def setup_method(self):
        self.shortener = URLShortener()

    def test_shorten_valid_url(self):
        request = ShortenRequest(url="https://google.com")
        response = self.shortener.shorten(request)

        assert response.original_url == "https://google.com"
        assert len(response.short_code) == 7
```

#### Integration Tests

**Focus**: Component interactions and data flow

```python
def test_shorten_and_expand_workflow():
    shortener = URLShortener()

    # Test complete workflow
    request = ShortenRequest(url="https://example.com")
    response = shortener.shorten(request)
    expanded = shortener.expand(response.short_code)

    assert expanded == "https://example.com"
```

#### Property-Based Testing (Planned)

**Tool**: Hypothesis

```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1))
def test_url_validation_never_crashes(random_input):
    shortener = URLShortener()
    # Should never crash, only return True/False
    result = shortener._is_valid_url(random_input)
    assert isinstance(result, bool)
```

### Coverage Requirements

- **Unit Tests**: >95% line coverage
- **Integration Tests**: 100% of public API endpoints
- **Critical Paths**: 100% coverage for security-sensitive code

## Performance Considerations

### Core Library Performance

**Target Metrics**:

- URL Shortening: <10ms per operation
- URL Expansion: <5ms per operation
- Memory Usage: <1MB per 10,000 URLs
- Throughput: >1000 operations/second

**Optimization Techniques**:

```python
# O(1) hash-based lookups
def expand(self, short_code: str) -> Optional[str]:
    # Dictionary lookup is O(1) average case
    if short_code not in self._urls:
        return None
```

### Memory Management

**Current Approach**: Simple in-memory dictionary

```python
# Memory-efficient storage structure
self._urls: dict[str, ShortURL] = {}

# ShortURL uses __slots__ for memory efficiency (planned)
@dataclass
class ShortURL:
    __slots__ = ['id', 'original_url', 'short_code', 'created_at',
                 'expires_at', 'click_count', 'is_active']
```

### Scalability Planning

**Storage Backend Strategy**:

```python
# Memory -> SQLite -> Redis progression
Phase 1: dict[str, ShortURL]           # 0-10K URLs
Phase 2: SQLite + LRU cache           # 10K-1M URLs
Phase 3: Redis + connection pooling    # 1M+ URLs
```

## Security Implementation

### Input Validation

**URL Validation**:

```python
def _is_valid_url(self, url: str) -> bool:
    """Comprehensive URL validation"""
    try:
        result = urlparse(url)
        # Check required components
        if not all([result.scheme, result.netloc]):
            return False
        # Validate scheme
        if result.scheme not in ('http', 'https'):
            return False
        # Additional validation...
        return True
    except Exception:
        return False
```

### Secure Code Generation

**Cryptographic Security**:

```python
import secrets
import string

def _generate_code(self, length: int = 7) -> str:
    """Cryptographically secure code generation"""
    alphabet = string.ascii_letters + string.digits  # 62 characters
    return ''.join(secrets.choice(alphabet) for _ in range(length))
    # 62^7 = 3,521,614,606,208 possible combinations
```

### Protection Against Attacks

#### Enumeration Protection

- **Random Code Generation**: No predictable patterns
- **Sufficient Entropy**: 7 characters = 22 bits of entropy
- **Rate Limiting** (planned): Prevent brute force attempts

#### Input Sanitization

```python
def shorten(self, request: ShortenRequest) -> ShortenResponse:
    # Validate all inputs
    if not self._is_valid_url(request.url):
        raise ValueError("Invalid URL provided")

    if request.custom_code:
        if not self._is_valid_short_code(request.custom_code):
            raise ValueError("Invalid custom code format")
```

## Error Handling

### Exception Hierarchy

```python
class TalisikError(Exception):
    """Base exception for all Talisik-related errors"""
    pass

class ValidationError(TalisikError):
    """Raised when input validation fails"""
    pass

class ConflictError(TalisikError):
    """Raised when short code already exists"""
    pass

class StorageError(TalisikError):
    """Raised when storage operations fail"""
    pass
```

### Error Response Strategy

```python
def shorten(self, request: ShortenRequest) -> ShortenResponse:
    try:
        # Main logic
        pass
    except ValidationError as e:
        # Log error details
        logger.warning(f"Validation failed: {e}")
        raise  # Re-raise for caller handling
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error: {e}")
        raise StorageError("Internal processing error")
```

## Configuration Management

### Environment Variables

```python
# Development
TALISIK_BASE_URL=http://localhost:3000
TALISIK_CODE_LENGTH=7
TALISIK_STORAGE=memory

# Production
TALISIK_BASE_URL=https://short.example.com
TALISIK_CODE_LENGTH=8
TALISIK_STORAGE=redis://redis:6379/0
TALISIK_REDIS_MAX_CONNECTIONS=20
```

### Configuration Classes (Planned)

```python
@dataclass
class TalisikConfig:
    base_url: str = "http://localhost:3000"
    default_code_length: int = 7
    max_custom_code_length: int = 50
    storage_backend: str = "memory"
    enable_analytics: bool = True

    @classmethod
    def from_env(cls) -> 'TalisikConfig':
        return cls(
            base_url=os.getenv('TALISIK_BASE_URL', cls.base_url),
            default_code_length=int(os.getenv('TALISIK_CODE_LENGTH', cls.default_code_length)),
            # ... other fields
        )
```

## Build and Deployment

### Package Configuration

**Setup**: `setup.py` with optional dependencies

```python
setup(
    name="talisik-short-url",
    install_requires=["pydantic>=2.0.0"],
    extras_require={
        "api": ["fastapi>=0.100.0", "uvicorn[standard]>=0.20.0"],
        "dev": ["pytest>=7.0.0", "pytest-cov>=4.0.0", "black>=23.0.0", "ruff>=0.1.0"],
        "redis": ["redis>=4.5.0"],
        "sqlite": ["aiosqlite>=0.19.0"],
    }
)
```

### Development Scripts

**Makefile**: Standardized development commands

```makefile
install:
	pip install -e ".[dev]"

test:
	pytest -v

lint:
	ruff check talisik/ tests/
	black --check talisik/ tests/

format:
	black talisik/ tests/
	ruff --fix talisik/ tests/
```

### Distribution Strategy

```bash
# Build distribution packages
python -m build

# Upload to PyPI (planned)
python -m twine upload dist/*

# Docker image (planned)
docker build -t talisik/short-url:latest .
```

## Integration Guidelines

### Library Usage

**Basic Integration**:

```python
from talisik import URLShortener, ShortenRequest

# Initialize shortener
shortener = URLShortener(base_url="https://yourdomain.com")

# Shorten URL
request = ShortenRequest(url="https://example.com/very/long/url")
response = shortener.shorten(request)
print(f"Short URL: {response.short_url}")

# Expand URL
original = shortener.expand(response.short_code)
print(f"Original: {original}")
```

**Advanced Configuration**:

```python
# With custom storage backend (planned)
from talisik.storage import RedisStorage

storage = RedisStorage(url="redis://localhost:6379/0")
shortener = URLShortener(storage=storage, base_url="https://short.ly")
```

### API Integration (Planned)

**FastAPI Integration**:

```python
from fastapi import FastAPI
from talisik import URLShortener

app = FastAPI()
shortener = URLShortener()

@app.post("/api/shorten")
async def shorten_url(request: ShortenRequest):
    return shortener.shorten(request)
```

## Monitoring and Debugging

### Logging Configuration

```python
import logging

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('talisik')
```

### Metrics Collection (Planned)

```python
from prometheus_client import Counter, Histogram

# Performance metrics
url_shortening_duration = Histogram('url_shortening_seconds')
url_expansion_duration = Histogram('url_expansion_seconds')

# Business metrics
urls_created = Counter('urls_created_total')
urls_accessed = Counter('urls_accessed_total')
```

### Health Checks (Planned)

```python
def health_check() -> dict:
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": __version__,
        "storage": {
            "type": self.storage.__class__.__name__,
            "status": "connected" if self.storage.is_healthy() else "error"
        }
    }
```

This technical documentation provides a comprehensive foundation for understanding and contributing to the Talisik Short URL project, following Kaizen principles of incremental improvement and clear, maintainable code.
