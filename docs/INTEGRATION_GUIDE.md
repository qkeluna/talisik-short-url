# 🔗 Talisik URL Shortener - Integration Guide

**Complete guide for integrating Talisik URL Shortener into your projects with correct BASE_URL configuration**

---

## 🎯 Quick Start

### **Correct Configuration for go.downlodr.com**

Your shortened URLs will be generated as: `https://go.downlodr.com/abc123`

---

## 📦 Installation

```bash
pip install talisik-shortener
```

---

## 🔧 Configuration Methods

### **Method 1: Environment Variables (Recommended)**

Create a `.env` file in your project:

```env
# Required for go.downlodr.com
BASE_URL=https://go.downlodr.com
XATA_API_KEY=your_xata_api_key
XATA_DATABASE_URL=your_xata_database_url
STORAGE_BACKEND=xata
```

Then use in your code:

```python
from talisik.core.shortener import URLShortener
from talisik.core.models import ShortenRequest

# Will automatically load from .env file
shortener = URLShortener()

# Shorten a URL
request = ShortenRequest(url="https://example.com")
result = shortener.shorten(request)

if result.success:
    print(f"Short URL: {result.short_url}")  # https://go.downlodr.com/abc123
    print(f"Short code: {result.short_code}")  # abc123
else:
    print(f"Error: {result.error}")
```

### **Method 2: Explicit Configuration**

```python
from talisik.core.shortener import URLShortener
from talisik.core.models import ShortenRequest

# Explicitly set base URL
shortener = URLShortener(base_url="https://go.downlodr.com")

# Or with full configuration
from talisik.core.config import TalisikConfig

config = TalisikConfig(
    xata_api_key="your_key",
    xata_database_url="your_url",
    base_url="https://go.downlodr.com",
    storage_backend="xata"
)

shortener = URLShortener(config=config)
```

### **Method 3: Runtime Environment**

```python
import os
os.environ["BASE_URL"] = "https://go.downlodr.com"

from talisik.core.shortener import URLShortener
shortener = URLShortener()  # Will use the environment variable
```

---

## 🚀 Common Usage Patterns

### **Basic URL Shortening**

```python
from talisik.core.shortener import URLShortener
from talisik.core.models import ShortenRequest

shortener = URLShortener(base_url="https://go.downlodr.com")

# Simple shortening
result = shortener.shorten(ShortenRequest(url="https://github.com"))
print(result.short_url)  # https://go.downlodr.com/xyz789

# Custom short code
result = shortener.shorten(ShortenRequest(
    url="https://docs.python.org",
    custom_code="python-docs"
))
print(result.short_url)  # https://go.downlodr.com/python-docs

# Expiring URL (expires in 24 hours)
result = shortener.shorten(ShortenRequest(
    url="https://temporary-link.com",
    expires_hours=24
))
```

### **URL Expansion and Info**

```python
# Expand short code to original URL
original_url = shortener.expand("xyz789")
print(original_url)  # https://github.com

# Get detailed information
info = shortener.get_info("xyz789")
print(info)
# {
#   "short_code": "xyz789",
#   "original_url": "https://github.com",
#   "created_at": "2024-01-15T10:30:00Z",
#   "click_count": 42,
#   "is_active": True,
#   "is_expired": False
# }
```

### **Statistics and Management**

```python
# Get usage statistics
stats = shortener.stats()
print(stats)
# {
#   "total_urls": 150,
#   "active_urls": 147,
#   "total_clicks": 1284
# }

# Deactivate a URL (soft delete)
shortener.deactivate("xyz789")

# Permanently delete a URL
shortener.delete("xyz789")
```

---

## 🐍 Framework Integration Examples

### **Flask Application**

```python
from flask import Flask, request, jsonify, redirect
from talisik.core.shortener import URLShortener
from talisik.core.models import ShortenRequest

app = Flask(__name__)
shortener = URLShortener(base_url="https://go.downlodr.com")

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    result = shortener.shorten(ShortenRequest(url=data['url']))

    if result.success:
        return jsonify({
            "short_url": result.short_url,
            "short_code": result.short_code
        })
    else:
        return jsonify({"error": result.error}), 400

@app.route('/<short_code>')
def redirect_to_url(short_code):
    original_url = shortener.expand(short_code)
    if original_url:
        return redirect(original_url)
    else:
        return "URL not found", 404
```

### **Django Application**

```python
# views.py
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from talisik.core.shortener import URLShortener
from talisik.core.models import ShortenRequest
import json

shortener = URLShortener(base_url="https://go.downlodr.com")

@csrf_exempt
def shorten_url(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        result = shortener.shorten(ShortenRequest(url=data['url']))

        if result.success:
            return JsonResponse({
                "short_url": result.short_url,
                "short_code": result.short_code
            })
        else:
            return JsonResponse({"error": result.error}, status=400)

def redirect_to_url(request, short_code):
    original_url = shortener.expand(short_code)
    if original_url:
        return HttpResponseRedirect(original_url)
    else:
        return JsonResponse({"error": "URL not found"}, status=404)
```

### **FastAPI Application**

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from talisik.core.shortener import URLShortener
from talisik.core.models import ShortenRequest

app = FastAPI()
shortener = URLShortener(base_url="https://go.downlodr.com")

class UrlRequest(BaseModel):
    url: str
    custom_code: str = None

@app.post("/shorten")
async def shorten_url(request: UrlRequest):
    result = shortener.shorten(ShortenRequest(
        url=request.url,
        custom_code=request.custom_code
    ))

    if result.success:
        return {
            "short_url": result.short_url,
            "short_code": result.short_code
        }
    else:
        raise HTTPException(status_code=400, detail=result.error)

@app.get("/{short_code}")
async def redirect_to_url(short_code: str):
    original_url = shortener.expand(short_code)
    if original_url:
        return RedirectResponse(url=original_url)
    else:
        raise HTTPException(status_code=404, detail="URL not found")
```

---

## 🔒 Security Best Practices

### **Environment Variables Protection**

```python
# ❌ Never hardcode credentials
shortener = URLShortener(base_url="https://go.downlodr.com")  # Missing API keys

# ✅ Use environment variables
import os
from talisik.core.config import TalisikConfig

config = TalisikConfig(
    xata_api_key=os.getenv("XATA_API_KEY"),
    xata_database_url=os.getenv("XATA_DATABASE_URL"),
    base_url="https://go.downlodr.com",
    storage_backend="xata"
)
```

### **URL Validation**

```python
from urllib.parse import urlparse

def is_safe_url(url: str) -> bool:
    """Validate URL before shortening"""
    try:
        parsed = urlparse(url)
        return all([
            parsed.scheme in ['http', 'https'],
            parsed.netloc,
            not parsed.netloc.startswith('localhost'),
            not parsed.netloc.startswith('127.0.0.1')
        ])
    except:
        return False

# Use in your application
if is_safe_url(user_url):
    result = shortener.shorten(ShortenRequest(url=user_url))
else:
    print("Invalid or unsafe URL")
```

---

## 🐛 Troubleshooting

### **Common Issues and Fixes**

#### **Issue: Wrong BASE_URL (https://downlodr.com instead of https://go.downlodr.com)**

```python
# ❌ Wrong: URLs generated as https://downlodr.com/abc123
shortener = URLShortener()  # Using wrong environment

# ✅ Fixed: URLs generated as https://go.downlodr.com/abc123
shortener = URLShortener(base_url="https://go.downlodr.com")

# Or set environment variable:
import os
os.environ["BASE_URL"] = "https://go.downlodr.com"
```

#### **Issue: Environment Variables Not Loading**

```python
# Make sure python-dotenv is installed
# pip install python-dotenv

from dotenv import load_dotenv
load_dotenv()  # Load .env file explicitly

from talisik.core.shortener import URLShortener
shortener = URLShortener()
```

#### **Issue: Xata Connection Errors**

```python
# Check your Xata credentials
import os
print("API Key:", os.getenv("XATA_API_KEY"))  # Should not be None
print("DB URL:", os.getenv("XATA_DATABASE_URL"))  # Should not be None

# Test with memory storage first
shortener = URLShortener(
    base_url="https://go.downlodr.com",
    storage_backend="memory"  # For testing
)
```

---

## 📊 Testing Your Integration

### **Simple Test Script**

```python
#!/usr/bin/env python3
"""Test your Talisik integration"""

import os
from talisik.core.shortener import URLShortener
from talisik.core.models import ShortenRequest

def test_integration():
    # Set up
    shortener = URLShortener(base_url="https://go.downlodr.com")

    # Test shortening
    result = shortener.shorten(ShortenRequest(url="https://github.com"))

    if result.success:
        print(f"✅ Short URL: {result.short_url}")

        # Verify correct base URL
        if result.short_url.startswith("https://go.downlodr.com/"):
            print("✅ Base URL is correct")
        else:
            print("❌ Base URL is wrong")

        # Test expansion
        original = shortener.expand(result.short_code)
        if original == "https://github.com":
            print("✅ URL expansion working")
        else:
            print("❌ URL expansion failed")
    else:
        print(f"❌ Error: {result.error}")

if __name__ == "__main__":
    test_integration()
```

---

## 📝 Environment File Template

Create `.env` in your project root:

```env
# Talisik URL Shortener Configuration
# Get credentials from https://xata.io dashboard

# Base URL - IMPORTANT: Use go.downlodr.com subdomain
BASE_URL=https://go.downlodr.com

# Xata Database (Required)
XATA_API_KEY=xau_your_api_key_here
XATA_DATABASE_URL=https://your-workspace.xata.sh/db/your-database

# Storage Backend
STORAGE_BACKEND=xata

# Optional: Feature Configuration
DEFAULT_CODE_LENGTH=7
MAX_CUSTOM_CODE_LENGTH=50
ENABLE_ANALYTICS=true
ENABLE_EXPIRATION=true

# Optional: Development Settings
DEBUG=false
LOG_LEVEL=INFO
```

---

## 📚 Next Steps

1. **Test locally** with the configuration above
2. **Deploy to production** with proper environment variables
3. **Monitor usage** with the built-in statistics
4. **Scale up** by upgrading your Xata plan as needed

---

## 🆘 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/frederickluna/talisik-short-url/issues)
- **Documentation**: Check the `/docs` folder for more guides
- **Examples**: See `/examples` for complete working applications

---

**Remember**: Always use `https://go.downlodr.com` as your BASE_URL for consistent short URL generation!
