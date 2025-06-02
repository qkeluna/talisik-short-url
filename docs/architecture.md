# Talisik Short URL - System Architecture

## Overview

Talisik Short URL follows a **Client SDK + Backend Service** architecture designed for maximum developer adoption and business scalability. The system provides a complete developer ecosystem with a Python backend service and an npm package client, similar to Firebase, Supabase, and Auth0.

> 📊 **Visual Workflows**: For detailed visual representations of how the URL shortener works, including flowcharts and sequence diagrams, see [Workflow Diagrams](workflow-diagram.md).

## Architectural Principles

### 1. Developer-First Design

- **npm Package Client**: Easy installation via `npm install talisik-shortener`
- **Multiple Framework Support**: React, Vue, Next.js, Svelte, Node.js
- **TypeScript-First**: Complete type safety and IntelliSense support
- **Zero Configuration**: Works out of the box with sensible defaults

### 2. Service-Oriented Architecture

- **Backend Service**: Python FastAPI server that you host/deploy
- **Client SDK**: JavaScript/TypeScript package that developers install
- **Clean API**: RESTful HTTP API with comprehensive OpenAPI documentation
- **Multi-tenant Ready**: API key authentication for different applications

### 3. Business Model Architecture

- **Open Source Core**: Python library and API server (GitHub)
- **Developer SDK**: npm package for easy integration (npmjs.com)
- **Hosted Service**: You provide the backend service (SaaS model)
- **Self-Hosted Option**: Developers can also self-host your backend

### 4. Kaizen Development Philosophy

- **Incremental complexity**: Start simple, add features progressively
- **Test-driven**: Each component has comprehensive test coverage
- **Developer Experience**: Focus on ease of use and integration
- **Documentation-first**: Every component is well-documented

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Developer Applications                             │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   React App     │   Vue App       │   Next.js App   │    Node.js Backend      │
│                 │                 │                 │                         │
│ npm install     │ npm install     │ npm install     │ npm install             │
│ talisik-        │ talisik-        │ talisik-        │ talisik-shortener       │
│ shortener       │ shortener       │ shortener       │                         │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                                    │
                          HTTP Requests (REST API)
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                     npm Package (talisik-shortener)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  • TalisikClient (Core API client)                                         │
│  • React Hooks (useTalisik, useTalisikClient)                              │
│  • TypeScript Types (Complete type definitions)                            │
│  • Error Handling (Custom error classes)                                   │
│  • Factory Functions (createTalisikClient, createDevClient)                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                            HTTPS API Calls
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Your Hosted Backend Service                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                     FastAPI REST API Server                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Endpoints:                                                         │   │
│  │  • POST /shorten      - Create short URL                           │   │
│  │  • GET /{code}        - Redirect to original URL                   │   │
│  │  • GET /info/{code}   - Get URL metadata and analytics             │   │
│  │  • GET /api/stats     - Get usage statistics                       │   │
│  │  • DELETE /api/{code} - Delete short URL                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│                       Core Python Library                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • URLShortener (Main business logic)                              │   │
│  │  • ShortURL, ShortenRequest, ShortenResponse (Data models)         │   │
│  │  • Code generation and validation                                  │   │
│  │  • Expiration and analytics logic                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│                        Storage Layer                                       │
│  ┌─────────────────┬─────────────────┬─────────────────────────────────┐   │
│  │   Memory        │     SQLite      │        Redis/PostgreSQL        │   │
│  │  (Current)      │    (Planned)    │         (Planned)               │   │
│  │                 │                 │                                 │   │
│  │ - Development   │ - Small/Medium  │ - Production Scale              │   │
│  │ - Fast          │ - Persistent    │ - High Performance              │   │
│  │ - Non-persistent│ - File-based    │ - Distributed                   │   │
│  └─────────────────┴─────────────────┴─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Client SDK Architecture (`packages/talisik-client`)

### 1. TalisikClient Class

**Location**: `packages/talisik-client/src/client.ts`

**Core Methods**:

```typescript
// URL Shortening
async shorten(request: ShortenRequest): Promise<ShortenResponse>

// URL Information
async getUrlInfo(shortCode: string): Promise<UrlInfo | null>
async expand(shortCode: string): Promise<string | null>
getRedirectUrl(shortCode: string): string

// Analytics
async getStats(): Promise<Stats>
```

**Features**:

- ✅ **Request/Response Transformation**: Converts camelCase ↔ snake_case
- ✅ **Error Handling**: Custom error classes with network detection
- ✅ **Timeout Support**: Configurable request timeouts with AbortController
- ✅ **Custom Headers**: Authentication and custom header support
- ✅ **TypeScript Support**: Complete type definitions and IntelliSense

### 2. React Integration

**Location**: `packages/talisik-client/src/hooks.ts`

**Hooks Available**:

```typescript
// High-level hook with state management
const { shortenUrl, getUrlInfo, getStats, loading, error } = useTalisik({
  baseUrl: "https://api.talisik.com",
});

// Low-level client hook
const client = useTalisikClient({
  baseUrl: "https://api.talisik.com",
});
```

**Features**:

- ✅ **Runtime React Detection**: Works without React dependency
- ✅ **Loading States**: Built-in loading and error state management
- ✅ **Error Boundaries**: Proper error propagation to React components
- ✅ **Memoization**: Optimized re-renders with useMemo and useCallback

### 3. TypeScript Definitions

**Location**: `packages/talisik-client/src/types.ts`

**Core Types**:

```typescript
// Configuration
interface TalisikConfig {
  baseUrl: string;
  apiKey?: string;
  headers?: Record<string, string>;
  timeout?: number;
}

// Request/Response Types
interface ShortenRequest {
  url: string;
  customCode?: string | null;
  expiresHours?: number | null;
}

interface ShortenResponse {
  shortUrl: string;
  originalUrl: string;
  shortCode: string;
  expiresAt?: string | null;
}

// Analytics Types
interface UrlInfo {
  shortCode: string;
  originalUrl: string;
  createdAt: string;
  expiresAt?: string | null;
  clickCount: number;
  isActive: boolean;
  isExpired: boolean;
}
```

### 4. Error Handling Architecture

**Location**: `packages/talisik-client/src/errors.ts`

**Error Hierarchy**:

```typescript
class TalisikError extends Error {
  // Base error class with status codes and details
}

class TalisikConfigError extends TalisikError {
  // Configuration and setup errors
}

class TalisikValidationError extends TalisikError {
  // Input validation errors
}
```

**Error Detection Methods**:

```typescript
error.isNetworkError(); // Network connectivity issues
error.isClientError(); // 4xx HTTP status codes
error.isServerError(); // 5xx HTTP status codes
error.isTimeout(); // Request timeout errors
```

### 5. Factory Functions

**Location**: `packages/talisik-client/src/factory.ts`

**Convenience Functions**:

```typescript
// Standard client
const client = createTalisikClient({ baseUrl: "https://api.talisik.com" });

// Development environment
const devClient = createDevClient();

// Production environment
const prodClient = createProdClient("https://api.talisik.com");
```

## Backend Service Architecture

### 1. FastAPI REST API

**Location**: `api/main.py`

**Current Endpoints**:

```python
POST /shorten              # Create short URL
GET  /{short_code}         # Redirect to original URL
GET  /info/{short_code}    # Get URL metadata
GET  /api/stats           # Get usage statistics
```

**Features**:

- ✅ **CORS Support**: Configured for React development (ports 3000, 5173)
- ✅ **OpenAPI Documentation**: Auto-generated Swagger docs
- ✅ **Pydantic Validation**: Request/response validation
- ✅ **Error Handling**: Consistent error responses

### 2. Core Library Integration

**Location**: `talisik/core/shortener.py`

The FastAPI endpoints wrap the core URLShortener class:

```python
from talisik.core.shortener import URLShortener

app = FastAPI()
shortener = URLShortener()

@app.post("/shorten")
async def shorten_url(request: ShortenURLRequest):
    result = shortener.shorten(request)
    return result
```

## Data Flow Architecture

### 1. URL Shortening Flow

```
Developer App (React/Vue/etc.)
    ↓
npm package: client.shorten({ url: 'https://example.com' })
    ↓
HTTP POST to: https://your-server.com/shorten
    ↓
FastAPI endpoint receives request
    ↓
Core URLShortener.shorten() processes
    ↓
Storage backend saves URL mapping
    ↓
Response: { shortUrl: 'https://your-server.com/abc123' }
    ↓
npm package returns typed ShortenResponse
    ↓
Developer app displays result to user
```

### 2. URL Expansion/Redirect Flow

```
User clicks: https://your-server.com/abc123
    ↓
Browser makes GET request
    ↓
FastAPI endpoint /{short_code}
    ↓
Core URLShortener.expand() lookups
    ↓
Analytics update (click count)
    ↓
HTTP 301/302 Redirect Response
    ↓
Browser redirects to original URL
```

### 3. Analytics Flow

```
Developer App requests analytics
    ↓
npm package: client.getUrlInfo('abc123')
    ↓
HTTP GET to: https://your-server.com/info/abc123
    ↓
FastAPI returns URL metadata
    ↓
npm package returns typed UrlInfo
    ↓
Developer app displays analytics
```

## Deployment Architecture

### 1. npm Package Distribution

**Build Process**:

```bash
cd packages/talisik-client
npm run build    # Creates dist/ with ESM + CommonJS builds
npm publish      # Publishes to npmjs.com
```

**Developer Installation**:

```bash
npm install talisik-shortener
```

**Package Contents**:

- `dist/index.js` - CommonJS build
- `dist/index.esm.js` - ES Modules build
- `dist/index.d.ts` - TypeScript declarations
- `README.md` - Usage documentation
- Package size: ~15.6 kB (excellent for npm package)

### 2. Backend Service Deployment

**Development**:

```bash
# Local development with hot reload
uvicorn api.main:app --reload --port 8000
```

**Production Options**:

- **Railway**: Simple git-based deployment
- **Vercel**: Serverless Python functions
- **Docker**: Container-based deployment
- **AWS/GCP/Azure**: Traditional cloud hosting
- **Self-hosted**: VPS or dedicated servers

**Environment Configuration**:

```env
# Production
TALISIK_BASE_URL=https://api.talisik.com
TALISIK_STORAGE=redis://redis:6379/0
CORS_ORIGINS=https://myapp.com,https://anotherapp.com

# Development
TALISIK_BASE_URL=http://localhost:8000
TALISIK_STORAGE=memory
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Business Model Architecture

### 1. Developer Adoption Strategy

**Free Tier**:

- npm package always free
- Self-hosting option available
- Open source core library

**Hosted Service Tiers**:

- **Starter**: 1,000 URLs/month, basic analytics
- **Pro**: 10,000 URLs/month, advanced analytics, custom domains
- **Enterprise**: Unlimited URLs, priority support, SLA

### 2. Monetization Paths

**SaaS Model**:

- Monthly subscriptions for hosted service
- Usage-based pricing for high-volume customers
- Premium features (custom domains, analytics, etc.)

**Enterprise**:

- On-premises deployment consulting
- Custom feature development
- Priority support contracts

### 3. Competitive Positioning

**vs. TinyURL/Bit.ly**:

- ✅ Developer-first with npm package
- ✅ Self-hosted option for privacy
- ✅ Full API control and customization

**vs. Firebase/Supabase**:

- ✅ Specialized for URL shortening use case
- ✅ Simpler integration
- ✅ Lower cost for URL shortening needs

## Security Architecture

### 1. Client-Side Security

**Input Validation**:

- URL validation before sending to server
- Custom code sanitization
- Request size limits

**API Security**:

- HTTPS enforcement
- API key authentication
- Request timeout protection
- CORS policy enforcement

### 2. Server-Side Security

**Authentication**:

- API key-based authentication
- Rate limiting per API key
- Request origin validation

**Data Protection**:

- No sensitive data in logs
- Configurable data retention
- Optional click tracking
- Privacy-focused defaults

### 3. Infrastructure Security

**Network Security**:

- HTTPS/TLS encryption
- Security headers (HSTS, CSP)
- DDoS protection via CloudFlare

**Data Security**:

- Encrypted storage options
- Regular backups
- Access logging and monitoring

## Performance Architecture

### 1. Client Performance

**npm Package Optimization**:

- Tree-shakeable exports
- Minimal bundle size (15.6 kB)
- ESM + CommonJS dual builds
- TypeScript for compile-time optimization

**Network Optimization**:

- Request deduplication
- Configurable timeouts
- Retry logic for failed requests
- Compression support

### 2. Server Performance

**API Performance**:

- FastAPI's high performance (comparable to NodeJS)
- Async/await throughout
- Minimal response payload
- Efficient JSON serialization

**Storage Performance**:

- O(1) URL lookups
- Memory-based caching
- Future: Redis for distributed caching
- Database indexing strategies

### 3. Scalability Strategy

**Horizontal Scaling**:

- Stateless API design
- Load balancer-friendly
- Database sharding by short code
- CDN for static assets

**Caching Strategy**:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Browser   │    │   API Cache │    │  Database   │
│   Cache     │    │   (Redis)   │    │ (Postgres)  │
│             │    │             │    │             │
│ 5min TTL    │ → │ 1hr TTL     │ → │ Persistent  │
│ Redirects   │    │ URL lookups │    │ Storage     │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Future Architecture Evolution

### 1. Advanced Analytics

**Planned Features**:

- Geographic click tracking
- Referrer analytics
- Custom event tracking
- Real-time dashboards

**Architecture**:

```typescript
// Enhanced analytics in npm package
interface DetailedAnalytics {
  clicks: ClickEvent[];
  geoData: GeographicData;
  referrers: ReferrerData;
  timeSeriesData: TimeSeriesData;
}
```

### 2. Enterprise Features

**Multi-tenant Architecture**:

- Organization-based API keys
- Team collaboration features
- Custom domain support
- White-label solutions

**Advanced Security**:

- OAuth2 integration
- SAML authentication
- Audit logging
- Compliance features (GDPR, etc.)

### 3. Platform Expansion

**Additional Language SDKs**:

- Python SDK (for backend applications)
- Go SDK (for microservices)
- PHP SDK (for legacy applications)
- Mobile SDKs (React Native, Flutter)

**Integration Ecosystem**:

- Zapier integrations
- Webhook support
- Third-party analytics integration
- CMS plugins (WordPress, etc.)

This architecture provides a solid foundation for the current implementation while enabling smooth evolution toward more complex deployments and features as the project grows following Kaizen principles, with a strong focus on developer adoption through the npm package ecosystem.
