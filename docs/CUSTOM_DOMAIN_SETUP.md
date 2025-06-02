# 🌐 Custom Domain Setup: downlodr.com

**Complete guide for implementing your custom domain with Talisik URL Shortener**

---

## 🎯 GOAL: Transform URLs from `localhost:8000/abc123` → `downlodr.com/abc123`

---

## 📋 OVERVIEW

With `downlodr.com`, your shortened URLs will look like:

- ✅ `downlodr.com/abc123` ← Professional, trustworthy
- ❌ `localhost:8000/abc123` ← Development only

**Benefits:**

- 🔗 **Shorter URLs**: `downlodr.com` vs `localhost:8000`
- 🛡️ **Trust**: Users trust branded domains
- 📊 **Analytics**: Better tracking with consistent domain
- 🚀 **SEO**: Your domain gets link juice

---

## 🚀 IMPLEMENTATION PHASES

### **Phase 1: Domain DNS Configuration (5 minutes)**

#### **Step 1: Choose Your Hosting Platform**

**Option A: Railway (Recommended for simplicity)**

```bash
# 1. Deploy to Railway first
npm install -g @railway/cli
railway login
railway init
railway up

# 2. Get your Railway URL (something like: abc123.railway.app)
# 3. Add custom domain in Railway dashboard
```

**Option B: Vercel (Great for static + API)**

```bash
# 1. Deploy API to Vercel
npx vercel

# 2. Add custom domain in Vercel dashboard
```

**Option C: Heroku**

```bash
# 1. Deploy to Heroku
heroku create your-app-name

# 2. Add custom domain
heroku domains:add downlodr.com
heroku domains:add www.downlodr.com
```

#### **Step 2: Configure DNS Records**

**In your domain registrar (GoDaddy, Namecheap, Cloudflare, etc.):**

```dns
# For Railway/Vercel/Heroku:
Type: CNAME
Name: @
Value: your-app-url.railway.app (or platform-specific URL)

# Alternative A Record (if CNAME doesn't work):
Type: A
Name: @
Value: [IP address provided by hosting platform]

# For www subdomain:
Type: CNAME
Name: www
Value: downlodr.com
```

**For Railway specifically:**

1. Go to Railway dashboard → Your project → Settings → Domains
2. Click "Add Domain"
3. Enter `downlodr.com`
4. Follow the DNS instructions provided

#### **Step 3: SSL/HTTPS Configuration**

Most modern platforms auto-provision SSL certificates:

- ✅ **Railway**: Automatic Let's Encrypt
- ✅ **Vercel**: Automatic SSL
- ✅ **Heroku**: Add SSL addon if needed

---

### **Phase 2: Application Configuration (2 minutes)**

#### **Update Environment Variables**

**In your hosting platform dashboard, set:**

```env
# CRITICAL: Update BASE_URL
BASE_URL=https://downlodr.com

# Keep other settings
XATA_API_KEY=your_actual_key
XATA_DATABASE_URL=your_actual_url
STORAGE_BACKEND=xata

# Update CORS for your domain
CORS_ORIGINS=https://downlodr.com,https://www.downlodr.com,http://localhost:3000

# Production settings
DEBUG=false
LOG_LEVEL=WARNING
```

#### **Update Local Configuration**

**Create `.env.production`:**

```env
# Production environment for downlodr.com
BASE_URL=https://downlodr.com
XATA_API_KEY=your_actual_key
XATA_DATABASE_URL=your_actual_url
STORAGE_BACKEND=xata
DEBUG=false
LOG_LEVEL=WARNING
CORS_ORIGINS=https://downlodr.com,https://www.downlodr.com
```

---

### **Phase 3: Code Updates (if needed)**

#### **API Configuration**

**In `api/main.py`, ensure CORS is dynamic:**

```python
import os

# Update CORS middleware to use environment variable
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Update base URL configuration
base_url = os.getenv("BASE_URL", "http://localhost:8000")
```

#### **Client Configuration**

**For frontend apps using your API:**

```typescript
// In your React/Vue/Next.js app
const API_BASE_URL = process.env.REACT_APP_API_URL || "https://downlodr.com";

const client = new TalisikClient({
  baseUrl: "https://downlodr.com",
});
```

#### **npm Package Update**

**Update default in `packages/talisik-client/src/factory.ts`:**

```typescript
export function createProdClient(
  overrides: Partial<TalisikConfig> = {}
): TalisikClient {
  return new TalisikClient({
    baseUrl: "https://downlodr.com", // Your custom domain
    timeout: 10000,
    ...overrides,
  });
}
```

---

### **Phase 4: Testing & Verification (5 minutes)**

#### **Step 1: DNS Propagation Check**

```bash
# Check if DNS is working
nslookup downlodr.com

# Check if HTTPS is working
curl -I https://downlodr.com
```

#### **Step 2: API Endpoint Testing**

```bash
# Test all endpoints with your custom domain
curl -X GET "https://downlodr.com/"

# Test URL shortening
curl -X POST "https://downlodr.com/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'

# Test redirect (should work)
curl -X GET "https://downlodr.com/[short_code]" -I
```

#### **Step 3: Full Integration Test**

**Create `test_custom_domain.py`:**

```python
#!/usr/bin/env python3
"""Test custom domain integration"""

import requests
import json

BASE_URL = "https://downlodr.com"

def test_custom_domain():
    print("🌐 Testing Custom Domain: downlodr.com")
    print("=" * 50)

    try:
        # Test 1: Root endpoint
        print("\n📝 Test 1: API Root")
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        # Test 2: Shorten URL
        print("\n📝 Test 2: Shorten URL")
        shorten_data = {"url": "https://github.com"}
        response = requests.post(f"{BASE_URL}/shorten", json=shorten_data)
        result = response.json()
        print(f"Short URL: {result['short_url']}")

        # Verify the short URL uses your custom domain
        assert result['short_url'].startswith("https://downlodr.com/")
        print("✅ Custom domain working correctly!")

        # Test 3: Test redirect
        short_code = result['short_code']
        print(f"\n📝 Test 3: Test Redirect")
        response = requests.get(f"{BASE_URL}/{short_code}", allow_redirects=False)
        print(f"Redirect Status: {response.status_code}")
        print(f"Location: {response.headers.get('location')}")

        print("\n🎉 All custom domain tests passed!")

    except Exception as e:
        print(f"❌ Error testing custom domain: {e}")

if __name__ == "__main__":
    test_custom_domain()
```

---

## 🔧 PLATFORM-SPECIFIC GUIDES

### **Railway Implementation**

```bash
# 1. Deploy to Railway
railway login
railway init
railway up

# 2. Add custom domain in Railway dashboard:
# → Go to your project
# → Settings → Domains
# → Add "downlodr.com"
# → Follow DNS instructions

# 3. Set environment variables:
railway variables set BASE_URL=https://downlodr.com
railway variables set XATA_API_KEY=your_key
railway variables set XATA_DATABASE_URL=your_url
```

### **Vercel Implementation**

```bash
# 1. Deploy to Vercel
npx vercel

# 2. Add custom domain:
# → Go to Vercel dashboard
# → Your project → Settings → Domains
# → Add "downlodr.com"

# 3. Set environment variables in Vercel dashboard
```

### **Heroku Implementation**

```bash
# 1. Deploy to Heroku
heroku create downlodr-api

# 2. Add custom domain
heroku domains:add downlodr.com

# 3. Set environment variables
heroku config:set BASE_URL=https://downlodr.com
heroku config:set XATA_API_KEY=your_key
```

---

## 🛡️ SECURITY CONSIDERATIONS

### **SSL/HTTPS Enforcement**

**In `api/main.py`, add security middleware:**

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Force HTTPS in production
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["downlodr.com", "www.downlodr.com"]
    )
```

### **Security Headers**

```python
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

## 🎯 FINAL CONFIGURATION

### **Updated Environment Variables**

```env
# Production configuration for downlodr.com
BASE_URL=https://downlodr.com
XATA_API_KEY=your_actual_key
XATA_DATABASE_URL=your_actual_url
STORAGE_BACKEND=xata
DEBUG=false
LOG_LEVEL=WARNING
CORS_ORIGINS=https://downlodr.com,https://www.downlodr.com
ENVIRONMENT=production
```

### **Updated npm Package Configuration**

**Users will now use:**

```typescript
import { TalisikClient } from "talisik-shortener";

const client = new TalisikClient({
  baseUrl: "https://downlodr.com",
});

// URLs will be generated as: https://downlodr.com/abc123
const result = await client.shorten({ url: "https://example.com" });
console.log(result.shortUrl); // "https://downlodr.com/abc123"
```

---

## 🚀 DEPLOYMENT TIMELINE

### **Total Time: ~30 minutes**

1. **DNS Configuration** (10 minutes)

   - Add CNAME/A records
   - Wait for propagation

2. **Platform Setup** (10 minutes)

   - Deploy to hosting platform
   - Add custom domain
   - Configure SSL

3. **Environment Update** (5 minutes)

   - Update BASE_URL
   - Update CORS origins

4. **Testing** (5 minutes)
   - Test all endpoints
   - Verify redirects work
   - Check HTTPS

---

## 📋 CUSTOM DOMAIN CHECKLIST

### **Pre-Deployment**

- [ ] Choose hosting platform (Railway recommended)
- [ ] Prepare environment variables
- [ ] Update CORS configuration

### **DNS Configuration**

- [ ] Add CNAME record pointing to hosting platform
- [ ] Add www subdomain if desired
- [ ] Verify DNS propagation (`nslookup downlodr.com`)

### **Platform Configuration**

- [ ] Deploy application to hosting platform
- [ ] Add custom domain in platform dashboard
- [ ] Configure SSL certificate (usually automatic)
- [ ] Set environment variable: `BASE_URL=https://downlodr.com`

### **Testing**

- [ ] Test API root: `curl https://downlodr.com/`
- [ ] Test URL shortening endpoint
- [ ] Test redirect functionality
- [ ] Verify HTTPS works correctly
- [ ] Test CORS with frontend applications

### **Client Updates**

- [ ] Update npm package default URLs
- [ ] Update documentation examples
- [ ] Inform users of new domain

---

## 🎉 RESULT

After implementation, your URL shortener will generate professional URLs like:

- `downlodr.com/abc123` ← Your branded short URLs
- `downlodr.com/github` ← Custom codes
- `downlodr.com/docs` ← API documentation

**Benefits achieved:**

- ✅ Professional branding
- ✅ Shorter, cleaner URLs
- ✅ Better user trust
- ✅ SEO benefits
- ✅ Analytics consistency

---

Would you like me to help you with any specific step of this implementation?
