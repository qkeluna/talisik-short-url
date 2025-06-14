# Talisik URL Shortener - JavaScript/TypeScript Client

[![npm version](https://badge.fury.io/js/talisik-shortener.svg)](https://www.npmjs.com/package/talisik-shortener)
[![TypeScript](https://img.shields.io/badge/TypeScript-Ready-blue.svg)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-Compatible-blue.svg)](https://reactjs.org/)

The official JavaScript/TypeScript client for [Talisik URL Shortener](https://github.com/frederickluna/talisik-short-url) - a privacy-focused URL shortening service.

**Created by [Erick Luna](https://github.com/frederickluna)**

## 🚀 Quick Start

### Installation

```bash
# With npm
npm install talisik-shortener

# With yarn
yarn add talisik-shortener

# With pnpm
pnpm add talisik-shortener
```

### Basic Usage

```typescript
import { TalisikClient } from "talisik-shortener";

// Create a client instance
const client = new TalisikClient({
  baseUrl: "https://go.downlodr.com", // Your custom subdomain
});

// Shorten a URL
const result = await client.shorten({
  url: "https://example.com",
});

console.log(result.shortUrl); // https://go.downlodr.com/abc123
```

## 📖 Usage Examples

### JavaScript (CommonJS)

```javascript
const { TalisikClient } = require("talisik-shortener");

const client = new TalisikClient({
  baseUrl: "https://api.yourdomain.com",
});

async function shortenUrl() {
  try {
    const result = await client.shorten({
      url: "https://example.com",
      customCode: "my-link",
      expiresHours: 24,
    });

    console.log("Short URL:", result.shortUrl);
  } catch (error) {
    console.error("Error:", error.message);
  }
}
```

### TypeScript

```typescript
import {
  TalisikClient,
  ShortenRequest,
  ShortenResponse,
} from "talisik-shortener";

const client = new TalisikClient({
  baseUrl: "https://api.yourdomain.com",
  timeout: 10000,
});

async function shortenUrl(request: ShortenRequest): Promise<ShortenResponse> {
  return await client.shorten(request);
}
```

### React with TypeScript

```tsx
import React, { useState } from "react";
import { TalisikClient, ShortenResponse } from "talisik-shortener";

const client = new TalisikClient({
  baseUrl: "https://api.yourdomain.com",
});

function UrlShortener() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<ShortenResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleShorten = async () => {
    setLoading(true);
    try {
      const shortened = await client.shorten({ url });
      setResult(shortened);
    } catch (error) {
      console.error("Failed to shorten URL:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter URL to shorten"
      />
      <button onClick={handleShorten} disabled={loading}>
        {loading ? "Shortening..." : "Shorten URL"}
      </button>

      {result && (
        <div>
          <p>
            Short URL: <a href={result.shortUrl}>{result.shortUrl}</a>
          </p>
          <p>Original: {result.originalUrl}</p>
        </div>
      )}
    </div>
  );
}
```

### Vue 3 + TypeScript

````vue
<template>
  <div>
    <input v-model="url" placeholder="Enter URL to shorten" />
    <button @click="shortenUrl" :disabled="loading">
      {{ loading ? "Shortening..." : "Shorten URL" }}
    </button>

    <div v-if="result">
      <p>
        Short URL: <a :href="result.shortUrl">{{ result.shortUrl }}</a>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { TalisikClient, type ShortenResponse } from "talisik-shortener";

const client = new TalisikClient({
  baseUrl: "https://api.yourdomain.com",
});

const url = ref("");
const result = ref<ShortenResponse | null>(null);
const loading = ref(false);

async function shortenUrl() {
  loading.value = true;
  try {
    result.value = await client.shorten({ url: url.value });
  } catch (error) {
    console.error("Failed to shorten URL:", error);
  } finally {
    loading.value = false;
  }
}
</script>

### URL Management & Table Display ```typescript import { TalisikClient } from
"talisik-shortener"; const client = new TalisikClient({ baseUrl:
"https://api.yourdomain.com", }); // Get all URLs for admin dashboard or
analytics async function loadUrlTable() { try { const urls = await
client.getAllUrls(); console.log(`Total URLs: ${urls.length}`); // Display in
table format urls.forEach(url => { console.log(`${url.short_code} ->
${url.original_url} (${url.click_count} clicks)`); }); // Filter active URLs
const activeUrls = urls.filter(url => url.is_active); // Filter by expiration
const permanentUrls = urls.filter(url => !url.expires_at); return urls; } catch
(error) { console.error("Failed to load URLs:", error); return []; } } // React
component for URL management function UrlManagementTable() { const [urls,
setUrls] = useState([]); const [loading, setLoading] = useState(true);
useEffect(() => { loadUrlTable().then(data => { setUrls(data);
setLoading(false); }); }, []); if (loading) return
<div>Loading...</div>
; return (
<table>
      <thead>
        <tr>
          <th>Short Code</th>
          <th>Original URL</th>
          <th>Clicks</th>
          <th>Status</th>
          <th>Created</th>
        </tr>
      </thead>
      <tbody>
        {urls.map(url => (
          <tr key={url.short_code}>
            <td>{url.short_code}</td>
            <td>{url.original_url}</td>
            <td>{url.click_count}</td>
            <td>{url.is_active ? '✅ Active' : '❌ Inactive'}</td>
            <td>{new Date(url.created_at).toLocaleDateString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
); }
````

### Next.js API Route

```typescript
// pages/api/shorten.ts
import { NextApiRequest, NextApiResponse } from "next";
import { TalisikClient } from "talisik-shortener";

const client = new TalisikClient({
  baseUrl: process.env.TALISIK_API_URL!,
});

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const { url } = req.body;
    const result = await client.shorten({ url });
    res.status(200).json(result);
  } catch (error) {
    res.status(500).json({ error: "Failed to shorten URL" });
  }
}
```

## 🎯 API Reference

### TalisikClient

#### Constructor

```typescript
new TalisikClient(config: TalisikConfig)
```

##### TalisikConfig

| Property  | Type                     | Required | Default | Description                         |
| --------- | ------------------------ | -------- | ------- | ----------------------------------- |
| `baseUrl` | `string`                 | ✅       | -       | Base URL of your Talisik API server |
| `apiKey`  | `string`                 | ❌       | -       | API key for authentication          |
| `timeout` | `number`                 | ❌       | `10000` | Request timeout in milliseconds     |
| `headers` | `Record<string, string>` | ❌       | `{}`    | Custom headers                      |

#### Methods

##### `shorten(request, options?)`

Shorten a URL.

```typescript
await client.shorten({
  url: "https://example.com",
  customCode: "my-link", // Optional
  expiresHours: 24, // Optional
});
```

**Returns**: `Promise<ShortenResponse>`

##### `getUrlInfo(shortCode, options?)`

Get information about a shortened URL.

```typescript
const info = await client.getUrlInfo("abc123");
```

**Returns**: `Promise<UrlInfo | null>`

##### `getStats(options?)`

Get overall statistics.

```typescript
const stats = await client.getStats();
```

**Returns**: `Promise<Stats>`

##### `getAllUrls(options?)`

Get all shortened URLs for table/list display. Returns an array of URL records with columns: original_url, short_code, expires_at, click_count, is_active, created_at.

```typescript
const urls = await client.getAllUrls();
console.log(`Found ${urls.length} URLs`);

// Example response:
// [
//   {
//     "original_url": "https://example.com",
//     "short_code": "abc123",
//     "expires_at": null,
//     "click_count": 5,
//     "is_active": true,
//     "created_at": "2024-01-01T12:00:00Z"
//   }
// ]
```

**Returns**: `Promise<Array<UrlRecord>>`

##### `expand(shortCode, options?)`

Get the original URL for a short code.

```typescript
const originalUrl = await client.expand("abc123");
```

**Returns**: `Promise<string | null>`

##### `getRedirectUrl(shortCode)`

Get the full redirect URL without making a request.

```typescript
const redirectUrl = client.getRedirectUrl("abc123");
// Returns: https://api.yourdomain.com/abc123
```

**Returns**: `string`

## 🔧 Configuration

### Custom Domain Setup

To use your own domain for the URL shortener:

**⚠️ Important**: If you already have a website at your root domain, use a **subdomain** to avoid breaking your existing site.

#### **Option 1: Subdomain (Recommended for existing websites)**

```
# DNS Configuration
Record Type: A
Name: go (creates go.yourdomain.com)
Value: your-platform-ip-address

# Results in URLs like: https://go.yourdomain.com/abc123
```

#### **Option 2: Root Domain (Only if domain is unused)**

```
# DNS Configuration
Record Type: A
Name: @ (uses root domain)
Value: your-platform-ip-address

# Results in URLs like: https://yourdomain.com/abc123
```

**Platform Configuration**: In your hosting platform (Leapcell, Vercel, etc.):

1. Add the custom domain/subdomain
2. Configure route rules to point to your service
3. Enable SSL certificate

**Update your client**:

```typescript
const client = new TalisikClient({
  baseUrl: "https://go.yourdomain.com", // Your subdomain
});
```

### Environment Variables

You can set default configuration using environment variables:

```bash
# .env
TALISIK_API_URL=https://api.yourdomain.com
TALISIK_API_KEY=your-api-key
```

### Development vs Production

```typescript
import { createDevClient, createProdClient } from "talisik-shortener";

// Development (uses localhost:8000)
const devClient = createDevClient();

// Production
const prodClient = createProdClient("https://api.yourdomain.com");
```

## ⚡ Advanced Usage

### Error Handling

```typescript
import { TalisikError } from "talisik-shortener";

try {
  const result = await client.shorten({ url: "invalid-url" });
} catch (error) {
  if (error instanceof TalisikError) {
    console.log("Status:", error.status);
    console.log("Code:", error.code);
    console.log("Is client error:", error.isClientError());
    console.log("Is not found:", error.isNotFound());
  }
}
```

### Request Options

```typescript
// Custom timeout and headers for a specific request
const result = await client.shorten(
  { url: "https://example.com" },
  {
    timeout: 5000,
    headers: { "Custom-Header": "value" },
  }
);
```

### AbortController Support

```typescript
const controller = new AbortController();

// Cancel the request after 3 seconds
setTimeout(() => controller.abort(), 3000);

try {
  const result = await client.shorten(
    { url: "https://example.com" },
    { signal: controller.signal }
  );
} catch (error) {
  if (error.name === "AbortError") {
    console.log("Request was cancelled");
  }
}
```

## 🏗️ Setup Your Own Server

This client works with the Talisik URL Shortener Python API. To set up your own server:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/frederickluna/talisik-short-url
   cd talisik-short-url
   ```

2. **Start the API server:**

   ```bash
   make install
   make api
   # Server running at http://localhost:8000
   ```

3. **Use with your client:**
   ```typescript
   const client = new TalisikClient({
     baseUrl: "http://localhost:8000",
   });
   ```

For production deployment, see the [deployment guide](https://github.com/frederickluna/talisik-short-url#deployment).

## 🔗 Related Packages

- **Python Library**: Use directly in Python applications
- **CLI Tool**: Command-line interface for URL shortening
- **Docker Images**: Ready-to-deploy containers

## 📝 TypeScript Support

This package is written in TypeScript and includes comprehensive type definitions. No additional `@types/` packages needed!

```typescript
import type {
  TalisikConfig,
  ShortenRequest,
  ShortenResponse,
  UrlInfo,
  Stats,
  TalisikError,
} from "talisik-shortener";
```

## 👤 Author

**Erick Luna**

- GitHub: [@frederickluna](https://github.com/frederickluna)
- Project: [Talisik Short URL](https://github.com/frederickluna/talisik-short-url)

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](https://github.com/frederickluna/talisik-short-url/blob/main/CONTRIBUTING.md).

## 📄 License

MIT License - see [LICENSE](https://github.com/frederickluna/talisik-short-url/blob/main/LICENSE) file for details.

## 🔗 Links

- [GitHub Repository](https://github.com/frederickluna/talisik-short-url)
- [API Documentation](https://github.com/frederickluna/talisik-short-url/blob/main/docs/API.md)
- [Examples](https://github.com/frederickluna/talisik-short-url/tree/main/examples)
- [Issues](https://github.com/frederickluna/talisik-short-url/issues)
