# React.js Integration Guide for Talisik URL Shortener

This guide shows how to integrate the Talisik URL Shortener Python library into React.js projects. Following Kaizen principles, we'll start with the simplest approach and build up complexity gradually.

## Integration Approaches

### 1. API-First Integration (Recommended - Simplest Start)

The most practical approach: Use React to consume our FastAPI endpoints via HTTP requests.

#### Setup

1. **Start the Python API server:**

```bash
# In your talisik-short-url directory
make api
# or
cd api && python main.py
```

2. **Create React client code:**

```jsx
// src/services/urlShortener.js
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export class TalisikClient {
  async shortenUrl({ url, customCode = null, expiresHours = null }) {
    try {
      const response = await fetch(`${API_BASE_URL}/shorten`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url,
          custom_code: customCode,
          expires_hours: expiresHours,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to shorten URL");
      }

      return await response.json();
    } catch (error) {
      console.error("Error shortening URL:", error);
      throw error;
    }
  }

  async getUrlInfo(shortCode) {
    try {
      const response = await fetch(`${API_BASE_URL}/info/${shortCode}`);

      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        throw new Error("Failed to get URL info");
      }

      return await response.json();
    } catch (error) {
      console.error("Error getting URL info:", error);
      throw error;
    }
  }

  async getStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stats`);

      if (!response.ok) {
        throw new Error("Failed to get stats");
      }

      return await response.json();
    } catch (error) {
      console.error("Error getting stats:", error);
      throw error;
    }
  }

  // Helper method to get the redirect URL without following it
  getRedirectUrl(shortCode) {
    return `${API_BASE_URL}/${shortCode}`;
  }
}

export default new TalisikClient();
```

#### React Component Examples

```jsx
// src/components/UrlShortener.jsx
import React, { useState } from "react";
import talisikClient from "../services/urlShortener";

export function UrlShortener() {
  const [url, setUrl] = useState("");
  const [customCode, setCustomCode] = useState("");
  const [expiresHours, setExpiresHours] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await talisikClient.shortenUrl({
        url,
        customCode: customCode || null,
        expiresHours: expiresHours ? parseInt(expiresHours) : null,
      });

      setResult(response);
      setUrl("");
      setCustomCode("");
      setExpiresHours("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="url-shortener">
      <h2>Shorten Your URL</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="url">URL to shorten:</label>
          <input
            type="url"
            id="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            required
          />
        </div>

        <div>
          <label htmlFor="customCode">Custom short code (optional):</label>
          <input
            type="text"
            id="customCode"
            value={customCode}
            onChange={(e) => setCustomCode(e.target.value)}
            placeholder="my-custom-code"
          />
        </div>

        <div>
          <label htmlFor="expiresHours">Expires in hours (optional):</label>
          <input
            type="number"
            id="expiresHours"
            value={expiresHours}
            onChange={(e) => setExpiresHours(e.target.value)}
            placeholder="24"
            min="1"
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Shortening..." : "Shorten URL"}
        </button>
      </form>

      {error && <div className="error">Error: {error}</div>}

      {result && (
        <div className="result">
          <h3>URL Shortened Successfully!</h3>
          <p>
            <strong>Short URL:</strong>
            <a
              href={result.short_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              {result.short_url}
            </a>
          </p>
          <p>
            <strong>Original URL:</strong> {result.original_url}
          </p>
          <p>
            <strong>Short Code:</strong> {result.short_code}
          </p>
          {result.expires_at && (
            <p>
              <strong>Expires:</strong>{" "}
              {new Date(result.expires_at).toLocaleString()}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
```

```jsx
// src/components/UrlAnalytics.jsx
import React, { useState, useEffect } from "react";
import talisikClient from "../services/urlShortener";

export function UrlAnalytics() {
  const [shortCode, setShortCode] = useState("");
  const [urlInfo, setUrlInfo] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load overall stats
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const statsData = await talisikClient.getStats();
      setStats(statsData);
    } catch (error) {
      console.error("Failed to load stats:", error);
    }
  };

  const handleLookup = async (e) => {
    e.preventDefault();
    if (!shortCode.trim()) return;

    setLoading(true);
    try {
      const info = await talisikClient.getUrlInfo(shortCode);
      setUrlInfo(info);
    } catch (error) {
      setUrlInfo(null);
      console.error("Failed to get URL info:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="url-analytics">
      <h2>URL Analytics</h2>

      {/* Overall Stats */}
      {stats && (
        <div className="overall-stats">
          <h3>Overall Statistics</h3>
          <div className="stats-grid">
            <div>Total URLs: {stats.total_urls}</div>
            <div>Active URLs: {stats.active_urls}</div>
            <div>Total Clicks: {stats.total_clicks}</div>
          </div>
        </div>
      )}

      {/* Individual URL Lookup */}
      <div className="url-lookup">
        <h3>Look Up URL Info</h3>
        <form onSubmit={handleLookup}>
          <input
            type="text"
            value={shortCode}
            onChange={(e) => setShortCode(e.target.value)}
            placeholder="Enter short code (e.g., abc123)"
          />
          <button type="submit" disabled={loading}>
            {loading ? "Looking up..." : "Get Info"}
          </button>
        </form>

        {urlInfo && (
          <div className="url-details">
            <h4>URL Details</h4>
            <p>
              <strong>Short Code:</strong> {urlInfo.short_code}
            </p>
            <p>
              <strong>Original URL:</strong> {urlInfo.original_url}
            </p>
            <p>
              <strong>Created:</strong>{" "}
              {new Date(urlInfo.created_at).toLocaleString()}
            </p>
            <p>
              <strong>Click Count:</strong> {urlInfo.click_count}
            </p>
            <p>
              <strong>Status:</strong>{" "}
              {urlInfo.is_active ? "Active" : "Inactive"}
            </p>
            {urlInfo.expires_at && (
              <p>
                <strong>Expires:</strong>{" "}
                {new Date(urlInfo.expires_at).toLocaleString()}
              </p>
            )}
            {urlInfo.is_expired && (
              <p className="expired-warning">⚠️ This URL has expired</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
```

#### Custom React Hook (Advanced)

```jsx
// src/hooks/useTalisik.js
import { useState, useCallback } from "react";
import talisikClient from "../services/urlShortener";

export function useTalisik() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const shortenUrl = useCallback(async (urlData) => {
    setLoading(true);
    setError(null);

    try {
      const result = await talisikClient.shortenUrl(urlData);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getUrlInfo = useCallback(async (shortCode) => {
    setLoading(true);
    setError(null);

    try {
      const result = await talisikClient.getUrlInfo(shortCode);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getStats = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await talisikClient.getStats();
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    shortenUrl,
    getUrlInfo,
    getStats,
    loading,
    error,
  };
}
```

### 2. TypeScript Integration

For TypeScript React projects:

```typescript
// src/types/talisik.ts
export interface ShortenUrlRequest {
  url: string;
  customCode?: string | null;
  expiresHours?: number | null;
}

export interface ShortenUrlResponse {
  short_url: string;
  original_url: string;
  short_code: string;
  expires_at?: string | null;
}

export interface UrlInfo {
  short_code: string;
  original_url: string;
  created_at: string;
  expires_at?: string | null;
  click_count: number;
  is_active: boolean;
  is_expired: boolean;
}

export interface Stats {
  total_urls: number;
  active_urls: number;
  total_clicks: number;
}
```

```typescript
// src/services/urlShortener.ts
import {
  ShortenUrlRequest,
  ShortenUrlResponse,
  UrlInfo,
  Stats,
} from "../types/talisik";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

class TalisikClient {
  async shortenUrl(request: ShortenUrlRequest): Promise<ShortenUrlResponse> {
    const response = await fetch(`${API_BASE_URL}/shorten`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        url: request.url,
        custom_code: request.customCode,
        expires_hours: request.expiresHours,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to shorten URL");
    }

    return await response.json();
  }

  async getUrlInfo(shortCode: string): Promise<UrlInfo | null> {
    const response = await fetch(`${API_BASE_URL}/info/${shortCode}`);

    if (response.status === 404) {
      return null;
    }

    if (!response.ok) {
      throw new Error("Failed to get URL info");
    }

    return await response.json();
  }

  async getStats(): Promise<Stats> {
    const response = await fetch(`${API_BASE_URL}/api/stats`);

    if (!response.ok) {
      throw new Error("Failed to get stats");
    }

    return await response.json();
  }
}

export default new TalisikClient();
```

### 3. Next.js Integration (Server-Side Option)

For Next.js projects, you can create API routes that call the Python service:

```javascript
// pages/api/shorten.js (or app/api/shorten/route.js for App Router)
export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method not allowed" });
  }

  try {
    const response = await fetch("http://localhost:8000/shorten", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(req.body),
    });

    const data = await response.json();

    if (!response.ok) {
      return res.status(response.status).json(data);
    }

    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ message: "Internal server error" });
  }
}
```

## Setup Instructions

### Development Setup

1. **Clone and setup the Python backend:**

```bash
git clone <your-repo>
cd talisik-short-url
make install
make api  # Start API server on http://localhost:8000
```

2. **Create React app:**

```bash
npx create-react-app my-url-shortener
cd my-url-shortener
```

3. **Add environment variables:**

```bash
# .env.local
REACT_APP_API_URL=http://localhost:8000
```

4. **Install additional dependencies (optional):**

```bash
npm install axios  # Alternative to fetch
npm install @tanstack/react-query  # For advanced data fetching
```

### Production Considerations

1. **CORS Configuration:**
   Add CORS middleware to your FastAPI app:

```python
# api/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **Environment Variables:**

```bash
# Production environment
REACT_APP_API_URL=https://api.yourdomain.com
BASE_URL=https://yourdomain.com
```

## Alternative Approaches

### Option B: WebAssembly/Pyodide (Advanced)

For running Python directly in the browser:

```jsx
// Experimental - Run Python in browser
import { loadPyodide } from "pyodide";

export async function usePyodideShortener() {
  const pyodide = await loadPyodide();

  // Install and import your library
  await pyodide.runPython(`
    # This would require packaging your library for PyPI
    import micropip
    await micropip.install('talisik-short-url')
    
    from talisik.core.shortener import URLShortener
    shortener = URLShortener()
  `);

  return {
    shorten: (url) => pyodide.runPython(`shortener.shorten("${url}")`),
    expand: (code) => pyodide.runPython(`shortener.expand("${code}")`),
  };
}
```

### Option C: Microservice Architecture

Deploy the Python API as a separate service and consume it from multiple React apps:

```
React App 1  ─┐
React App 2  ─┼─→ Talisik API Service (Python)
React App 3  ─┘
```

## Kaizen Implementation Strategy

Start with **Option 1 (API Integration)** because:

1. **Immediate Value**: Works with existing code
2. **Separation of Concerns**: Clear backend/frontend boundaries
3. **Scalability**: Easy to deploy and scale separately
4. **Team Compatibility**: Frontend and backend teams can work independently

### Growth Path:

1. Start: Basic API integration with fetch
2. Add: Error handling and loading states
3. Enhance: Custom hooks and TypeScript
4. Scale: Add caching, optimistic updates, offline support
5. Advanced: Consider WebAssembly for special use cases

This approach lets you start using the library immediately while building toward more sophisticated integrations over time.
