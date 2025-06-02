# 🚀 Production Testing Guide

Complete guide for testing your deployed Talisik URL Shortener backend and npm client SDK.

## 📋 Prerequisites

1. **Backend deployed** to production (Leapcell, Heroku, Railway, etc.)
2. **npm client SDK** published to npmjs.com (already done: `talisik-shortener`)
3. **Production URL** of your deployed backend API

## 🎯 Quick Start

### Option 1: Automated Testing (Recommended)

```bash
# Test everything at once
make test-all-production URL=https://your-production-url.com

# Or test individually:
make test-production URL=https://your-production-url.com     # Backend API
make test-npm-client URL=https://your-production-url.com     # npm SDK
make setup-react-test                                        # React example
```

### Option 2: Manual Testing

1. **Install testing dependencies:**

   ```bash
   pip install -r requirements-test.txt
   ```

2. **Test backend API:**

   ```bash
   python test_production.py https://your-production-url.com
   ```

3. **Test npm client SDK:**
   ```bash
   npm install talisik-shortener
   node test_npm_client.js https://your-production-url.com
   ```

---

## 🧪 Test Suites Overview

### 1. Backend API Tests (`test_production.py`)

Tests all REST API endpoints:

| Test                    | Endpoint           | Purpose              |
| ----------------------- | ------------------ | -------------------- |
| Health Check            | `GET /`            | API availability     |
| URL Shortening (Auto)   | `POST /shorten`    | Auto-generated codes |
| URL Shortening (Custom) | `POST /shorten`    | Custom short codes   |
| URL Redirection         | `GET /{code}`      | HTTP redirects       |
| URL Info                | `GET /info/{code}` | Metadata retrieval   |
| Click Tracking          | `GET /{code}`      | Click counting       |
| API Statistics          | `GET /api/stats`   | Usage statistics     |
| Error Handling          | Various            | Invalid inputs       |

**Expected Output:**

```
🚀 Starting Production Test Suite for: https://your-app.com
============================================================
[PASS] Health Check
      API accessible, response: {'message': 'Talisik URL Shortener API', ...}

[PASS] Shorten URL (Auto)
      Created: https://your-app.com/abc123

[PASS] URL Redirect
      Redirects to: https://github.com/frederickluna/talisik-short-url

[PASS] Get URL Info
      Clicks: 1

[PASS] Click Tracking
      Clicks: 1 → 2

[PASS] Shorten URL (Custom)
      Created: https://your-app.com/test-1738123456

[PASS] API Stats
      URLs: 2, Clicks: 2

[PASS] Error Handling (Invalid URL)
      Properly rejects invalid URLs

[PASS] Error Handling (Not Found)
      Properly returns 404 for missing URLs

============================================================
📊 TEST SUMMARY
Total Tests: 9
✅ Passed: 9
❌ Failed: 0
Success Rate: 100.0%

🎉 All tests passed! Your production API is working perfectly.
```

### 2. npm Client SDK Tests (`test_npm_client.js`)

Tests the JavaScript/TypeScript client:

| Test                 | Method                              | Purpose              |
| -------------------- | ----------------------------------- | -------------------- |
| Client Instantiation | `new TalisikClient()`               | SDK initialization   |
| Shorten URL (Auto)   | `client.shorten()`                  | Auto-generated codes |
| Shorten URL (Custom) | `client.shorten(url, {customCode})` | Custom codes         |
| Expand URL           | `client.expand()`                   | URL expansion        |
| Get URL Info         | `client.getInfo()`                  | Metadata retrieval   |
| Get Stats            | `client.getStats()`                 | Usage statistics     |
| Error Handling       | Various                             | Invalid inputs       |
| TypeScript Support   | Type definitions                    | TS compatibility     |

**Expected Output:**

```
🚀 Starting Client SDK Test Suite for: https://your-app.com
[PASS] Client Instantiation
      TalisikClient created successfully

[PASS] Shorten URL (Auto)
      Created: https://your-app.com/def456

[PASS] Shorten URL (Custom)
      Created: https://your-app.com/sdk-test-1738123456

[PASS] Expand URL
      Original: https://github.com/frederickluna/talisik-short-url

[PASS] Get URL Info
      Clicks: 0

[PASS] Get Stats
      Total URLs: 4, Total Clicks: 2

[PASS] Error Handling (Invalid URL)
      Properly rejects invalid URLs

[PASS] Error Handling (Not Found)
      Properly handles missing URLs

[PASS] TypeScript Support
      All methods available with correct types

============================================================
📊 CLIENT SDK TEST SUMMARY
Total Tests: 9
✅ Passed: 9
❌ Failed: 0
Success Rate: 100.0%

🎉 All tests passed! Your npm client SDK is working perfectly.
```

### 3. React Integration Test

Interactive React application demonstrating SDK usage:

```bash
# Setup React test environment
make setup-react-test

# Run React test app
cd examples/react-test
REACT_APP_API_URL=https://your-production-url.com npm run dev
```

**Features:**

- ✅ URL shortening form
- ✅ Real-time statistics
- ✅ Click tracking
- ✅ Interactive SDK testing
- ✅ TypeScript integration
- ✅ Error handling demonstration

---

## 🔧 Integration Examples

### React/Next.js Integration

```typescript
import { TalisikClient } from "talisik-shortener";

const client = new TalisikClient({
  baseUrl: process.env.NEXT_PUBLIC_API_URL || "https://your-api.com",
});

export function useUrlShortener() {
  const [loading, setLoading] = useState(false);

  const shorten = async (url: string, customCode?: string) => {
    setLoading(true);
    try {
      const result = await client.shorten(url, { customCode });
      return result;
    } catch (error) {
      console.error("Shortening failed:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return { shorten, loading };
}
```

### Vue.js Integration

```javascript
import { TalisikClient } from "talisik-shortener";

export default {
  data() {
    return {
      client: new TalisikClient({
        baseUrl: process.env.VUE_APP_API_URL,
      }),
      shortenedUrls: [],
    };
  },
  methods: {
    async shortenUrl(url) {
      try {
        const result = await this.client.shorten(url);
        this.shortenedUrls.push(result);
        return result;
      } catch (error) {
        console.error("Failed to shorten URL:", error);
      }
    },
  },
};
```

### Node.js Backend Integration

```javascript
const { TalisikClient } = require("talisik-shortener");

const client = new TalisikClient({
  baseUrl: process.env.TALISIK_API_URL,
});

// Express.js middleware example
app.post("/api/shorten", async (req, res) => {
  try {
    const { url } = req.body;
    const result = await client.shorten(url);
    res.json(result);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});
```

---

## 🎯 Production Checklist

### ✅ Backend Deployment

- [ ] API deployed and accessible
- [ ] Health check endpoint responds
- [ ] Database (Xata.io) connected
- [ ] Environment variables configured
- [ ] CORS properly configured
- [ ] Error handling working

### ✅ npm Package

- [ ] Package published to npmjs.com
- [ ] TypeScript definitions included
- [ ] All methods working
- [ ] Error handling proper
- [ ] Documentation complete

### ✅ Testing

- [ ] All backend tests pass
- [ ] All client SDK tests pass
- [ ] React integration working
- [ ] Error scenarios handled
- [ ] Performance acceptable

---

## 🐛 Troubleshooting

### Common Issues

**1. Connection Refused**

```
❌ Health Check FAIL: Connection error: Cannot connect to host
```

- **Solution:** Check if your production URL is correct and accessible
- **Check:** Verify deployment is successful and not sleeping

**2. CORS Errors**

```
❌ Access to fetch at 'https://api.com' from origin 'http://localhost:3000' has been blocked by CORS
```

- **Solution:** Configure CORS in your FastAPI application:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**3. npm Package Not Found**

```
❌ Client Instantiation FAIL: Cannot find module 'talisik-shortener'
```

- **Solution:** Ensure the package is properly published:

```bash
npm publish  # If you haven't published yet
npm install talisik-shortener  # Test installation
```

**4. API Validation Errors**

```
❌ Shorten URL FAIL: Status: 422, Error: Validation error
```

- **Solution:** Check request format matches API expectations
- **Debug:** Use browser developer tools to inspect request/response

### Getting Help

1. **Check logs:** Review your production deployment logs
2. **Test locally:** Ensure everything works in development
3. **Verify environment:** Check all environment variables are set
4. **Network issues:** Test with curl or Postman first

---

## 📊 Performance Benchmarks

### Expected Response Times

| Endpoint     | Expected Time | Notes                    |
| ------------ | ------------- | ------------------------ |
| Health Check | < 100ms       | Simple response          |
| Shorten URL  | < 200ms       | Database write           |
| Redirect     | < 150ms       | Database read + redirect |
| Get Info     | < 100ms       | Database read            |
| Stats        | < 300ms       | Aggregate query          |

### Scalability Testing

```bash
# Install wrk for load testing
# Test 100 concurrent connections for 30 seconds
wrk -t12 -c100 -d30s --latency https://your-api.com/

# Test shortening endpoint
wrk -t4 -c10 -d10s -s scripts/shorten.lua https://your-api.com/shorten
```

---

## 🎉 Success Criteria

Your production deployment is ready when:

- ✅ **All tests pass** (100% success rate)
- ✅ **Performance acceptable** (< 500ms response times)
- ✅ **Error handling robust** (graceful failure modes)
- ✅ **Client SDK working** (all methods functional)
- ✅ **Integration examples** (React app working)

**You're now ready to integrate Talisik into production applications!** 🚀
