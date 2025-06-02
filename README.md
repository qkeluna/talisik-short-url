# Talisik Short URL

A privacy-focused URL shortener built with Python and FastAPI, inspired by tnyr.me. **Now available as an npm package for JavaScript developers!**

## 🚀 **For JavaScript/React Developers**

### **Installation (Like shadcn/ui)**

```bash
npm install talisik-shortener
```

### **Usage (Any Framework)**

```typescript
import { TalisikClient } from "talisik-shortener";

const client = new TalisikClient({
  baseUrl: "https://api.yourdomain.com",
});

// Shorten a URL
const result = await client.shorten({
  url: "https://example.com",
  customCode: "my-link",
  expiresHours: 24,
});

console.log(result.shortUrl); // Ready to use!
```

**Works with**: React, Vue, Next.js, Svelte, Node.js, and any JavaScript framework!

📚 **[Complete npm Package Documentation →](packages/talisik-client/README.md)**

---

## Features

- 🔗 **URL Shortening**: Generate short, memorable links
- 🎯 **Custom Codes**: Use your own custom short codes
- ⏰ **Expiration**: Set time-based URL expiration
- 📊 **Analytics**: Track clicks and usage statistics
- 🔒 **Privacy-Focused**: No tracking beyond basic analytics
- 🚀 **Fast API**: Built with FastAPI for high performance
- 📦 **Library + Service**: Use as Python library or web API
- ⚛️ **React Ready**: Easy integration with React/JavaScript frontends
- 🎯 **npm Package**: Install and use like any other JavaScript library

## Quick Start

### Option 1: JavaScript/React Developer (Recommended)

**5-minute setup** - Get URL shortening in your React/Vue/Next.js app:

```bash
# 1. Install the client
npm install talisik-shortener

# 2. Use in your app
import { TalisikClient } from 'talisik-shortener';
const client = new TalisikClient({ baseUrl: 'https://api.yourdomain.com' });
const result = await client.shorten({ url: 'https://example.com' });
```

**Backend options:**

- Use our hosted service (coming soon)
- Deploy your own (see below)

### Option 2: Python Developer

```bash
# 1. Clone and install
git clone <this-repo>
cd talisik-short-url
make install

# 2. Use as library
from talisik.core.shortener import URLShortener
shortener = URLShortener()
result = shortener.shorten("https://example.com")
```

### Option 3: API Service

```bash
# Start the API server
make api
# API available at http://localhost:8000

# Test it
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Architecture

### **🎯 Multi-Platform Support**

| Platform             | Installation                    | Usage                                             |
| -------------------- | ------------------------------- | ------------------------------------------------- |
| **JavaScript/React** | `npm install talisik-shortener` | `import { TalisikClient }`                        |
| **Python Library**   | `pip install .`                 | `from talisik.core.shortener import URLShortener` |
| **REST API**         | `make api`                      | `curl http://localhost:8000/shorten`              |
| **CLI Tool**         | `make install`                  | `python cli_demo.py`                              |

### **🏗️ Package Structure**

```
talisik-short-url/
├── 📦 packages/talisik-client/    # npm package for JavaScript
├── 🐍 talisik/                    # Python library
├── 🌐 api/                        # FastAPI REST service
├── 📚 docs/                       # Documentation
├── 🧪 tests/                      # Test suite
└── 📖 examples/                   # Usage examples
```

## Usage Examples

### **React Component**

```tsx
import React, { useState } from "react";
import { TalisikClient } from "talisik-shortener";

function UrlShortener() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);

  const client = new TalisikClient({
    baseUrl: "https://api.yourdomain.com",
  });

  const handleShorten = async () => {
    const shortened = await client.shorten({ url });
    setResult(shortened);
  };

  return (
    <div>
      <input
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter URL to shorten"
      />
      <button onClick={handleShorten}>Shorten</button>
      {result && <p>Short URL: {result.shortUrl}</p>}
    </div>
  );
}
```

### **Python Library**

```python
from talisik.core.shortener import URLShortener
from talisik.core.models import ShortenRequest

# Initialize shortener
shortener = URLShortener()

# Shorten a URL
request = ShortenRequest(
    url="https://example.com",
    custom_code="my-link",
    expires_hours=24
)
result = shortener.shorten(request)
print(f"Short URL: {result.short_url}")
```

### **REST API**

```bash
# Shorten URL
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "custom_code": "my-link",
    "expires_hours": 24
  }'

# Get URL info
curl "http://localhost:8000/info/my-link"

# Get statistics
curl "http://localhost:8000/api/stats"
```

## Framework Integration Examples

- **[React Integration Guide](docs/REACT_INTEGRATION.md)** - Complete React setup
- **[Vue.js Example](packages/talisik-client/README.md#vue-3--typescript)** - Vue 3 composition API
- **[Next.js API Routes](packages/talisik-client/README.md#nextjs-api-route)** - Server-side usage
- **[Node.js Backend](examples/npm-package-demo.js)** - Backend service integration

## Development

### **Available Commands**

```bash
make install        # Install Python dependencies
make test           # Run Python tests
make api            # Start API server
make demo-js        # Run JavaScript integration demo
make test-coverage  # Run tests with coverage
```

### **Project Status**

| Component         | Status      | Coverage               |
| ----------------- | ----------- | ---------------------- |
| 🐍 Python Library | ✅ Complete | 96%                    |
| 🌐 REST API       | ✅ Complete | 96%                    |
| 📦 npm Package    | ✅ Ready    | Documentation complete |
| 🧪 Test Suite     | ✅ Complete | 96% coverage           |
| 📚 Documentation  | ✅ Complete | All frameworks         |

## Deployment

### **npm Package Publishing**

```bash
cd packages/talisik-client
npm publish  # Publish to npm registry
```

### **API Server Deployment**

- **Local**: `make api`
- **Docker**: `docker build -t talisik-api .`
- **Cloud**: Deploy to Railway, Heroku, or AWS

See [Deployment Guide](docs/DEPLOYMENT.md) for details.

## Roadmap

### **Phase 1: Foundation** ✅

- [x] Core Python library
- [x] FastAPI REST service
- [x] npm package structure
- [x] Multi-framework support

### **Phase 2: Frontend** (Current)

- [ ] React web interface
- [ ] Admin dashboard
- [ ] Real-time analytics

### **Phase 3: Advanced Features**

- [ ] QR code generation
- [ ] Bulk operations
- [ ] Team collaboration
- [ ] Custom domains

### **Phase 4: Scale**

- [ ] Database persistence
- [ ] Caching layer
- [ ] Rate limiting
- [ ] Enterprise features

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### **Quick Start for Contributors**

```bash
# 1. Fork and clone
git clone <your-fork>
cd talisik-short-url

# 2. Set up development environment
make install
make test

# 3. Test the npm package
node examples/npm-package-demo.js
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **[npm Package](packages/talisik-client/)** - JavaScript/TypeScript client
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs
- **[Examples](examples/)** - Usage examples
- **[GitHub](https://github.com/your-username/talisik-short-url)** - Source code
