# Quick Start: React + Talisik URL Shortener

Get up and running with Talisik URL Shortener in your React app in 5 minutes.

## 1. Start the API (Terminal 1)

```bash
# Clone and start the Python API
git clone <your-repo>
cd talisik-short-url
make install
make api
# API now running at http://localhost:8000
```

## 2. Create React App (Terminal 2)

```bash
# Create a new React app
npx create-react-app my-shortener
cd my-shortener

# Add environment variable
echo "REACT_APP_API_URL=http://localhost:8000" > .env.local

# Start React app
npm start
# React app now running at http://localhost:3000
```

## 3. Add the URL Shortener Service

Create `src/urlShortener.js`:

```javascript
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export async function shortenUrl(url, customCode = null, expiresHours = null) {
  const response = await fetch(`${API_URL}/shorten`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
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

  return response.json();
}

export async function getUrlInfo(shortCode) {
  const response = await fetch(`${API_URL}/info/${shortCode}`);
  return response.ok ? response.json() : null;
}
```

## 4. Replace App.js

Replace the contents of `src/App.js`:

```jsx
import React, { useState } from "react";
import { shortenUrl, getUrlInfo } from "./urlShortener";
import "./App.css";

function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const shortened = await shortenUrl(url);
      setResult(shortened);
      setUrl("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🔗 Talisik URL Shortener</h1>

        <form onSubmit={handleSubmit} style={{ margin: "20px 0" }}>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            required
            style={{
              padding: "10px",
              fontSize: "16px",
              width: "300px",
              marginRight: "10px",
            }}
          />
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "10px 20px",
              fontSize: "16px",
              background: "#61dafb",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            {loading ? "Shortening..." : "Shorten"}
          </button>
        </form>

        {error && (
          <div style={{ color: "red", margin: "10px 0" }}>Error: {error}</div>
        )}

        {result && (
          <div
            style={{
              background: "#282c34",
              padding: "20px",
              borderRadius: "8px",
              margin: "20px 0",
            }}
          >
            <h3>✅ URL Shortened!</h3>
            <p>
              <strong>Short URL:</strong>{" "}
              <a
                href={result.short_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "#61dafb" }}
              >
                {result.short_url}
              </a>
            </p>
            <p>
              <strong>Original:</strong> {result.original_url}
            </p>
            <p>
              <strong>Code:</strong> {result.short_code}
            </p>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
```

## 5. Test It Out!

1. Enter a URL like `https://github.com`
2. Click "Shorten"
3. Click the generated short URL to test the redirect
4. Visit `http://localhost:8000/docs` to see the full API

## What You Just Built

- ✅ Full URL shortening functionality
- ✅ Custom short codes support
- ✅ URL expiration
- ✅ Click tracking
- ✅ Analytics via API endpoints
- ✅ Production-ready FastAPI backend
- ✅ Clean React frontend

## Next Steps

- **Add Analytics**: Use `getUrlInfo(shortCode)` to show click counts
- **Add Custom Codes**: Let users specify their own short codes
- **Add Expiration**: Let users set expiration times
- **Style It**: Add CSS or a UI library like Material-UI or Chakra UI
- **Deploy**: Deploy to Vercel (frontend) + Railway/Heroku (backend)

## API Endpoints Available

- `POST /shorten` - Create short URLs
- `GET /{shortCode}` - Redirect to original URL
- `GET /info/{shortCode}` - Get URL metadata
- `GET /api/stats` - Get usage statistics
- `GET /docs` - Interactive API documentation

You now have a fully functional URL shortener that's production-ready! 🎉
