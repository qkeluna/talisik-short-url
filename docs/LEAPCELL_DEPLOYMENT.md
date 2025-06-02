# 🚀 Leapcell.io Deployment Guide

**Complete guide for deploying Talisik Short URL to Leapcell.io with custom domain downlodr.com**

---

## 🎯 **PROBLEM SOLVED**

The error you encountered was because Leapcell.io expected:

1. ❌ `gunicorn` (was missing from requirements.txt)
2. ❌ Proper WSGI/ASGI configuration
3. ❌ Port 8080 instead of 8000

**✅ Fixed with these files:**

- `requirements.txt` - Added gunicorn
- `wsgi.py` - WSGI/ASGI adapter
- `Procfile` - Proper start command
- `start.sh` - Startup script
- `leapcell.yaml` - Platform configuration

---

## 🚀 **DEPLOYMENT STEPS**

### **Step 1: Verify Fixed Files**

Your project now has these new files:

```bash
# Check the files exist
ls -la requirements.txt wsgi.py Procfile start.sh leapcell.yaml

# Verify requirements.txt has gunicorn
grep "gunicorn" requirements.txt
```

### **Step 2: Deploy to Leapcell.io**

1. **Push your updated code** with the new files
2. **Redeploy** in Leapcell.io dashboard
3. **The deployment should now work** ✅

### **Step 3: Set Environment Variables**

In your Leapcell.io dashboard, set these environment variables:

```env
# Required for downlodr.com custom domain
BASE_URL=https://your-app-url.leapcell.io  # Update after getting URL
STORAGE_BACKEND=xata

# Xata Database (your existing credentials)
XATA_API_KEY=xau_0LqJC20AtrvuyYP6HY8bSxjeb1cyZuh96
XATA_DATABASE_URL=https://Khyle-Erick-Luna-s-workspace-8g1h14.us-east-1.xata.sh/db/kclick-db

# Production settings
DEBUG=false
LOG_LEVEL=WARNING
ENVIRONMENT=production

# CORS for custom domain (update after getting your Leapcell URL)
CORS_ORIGINS=https://your-app-url.leapcell.io,https://downlodr.com,https://www.downlodr.com
```

### **Step 4: Test the Deployment**

Once deployed, test these endpoints:

```bash
# Replace YOUR_LEAPCELL_URL with your actual deployed URL
export LEAPCELL_URL="https://your-app-url.leapcell.io"

# Test 1: API Root
curl "$LEAPCELL_URL/"

# Test 2: Shorten URL
curl -X POST "$LEAPCELL_URL/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/frederickluna/talisik-short-url"}'

# Test 3: Test redirect (use short_code from previous response)
curl -X GET "$LEAPCELL_URL/SHORT_CODE" -I
```

### **Step 5: Add Custom Domain (downlodr.com)**

Once your app is working on Leapcell.io:

1. **In Leapcell.io Dashboard:**

   - Go to your project settings
   - Add custom domain: `downlodr.com`
   - Get the CNAME target (e.g., `your-app.leapcell.io`)

2. **In your Domain Registrar:**

   ```dns
   Type: CNAME
   Name: @
   Value: your-app-url.leapcell.io

   # For www subdomain
   Type: CNAME
   Name: www
   Value: downlodr.com
   ```

3. **Update Environment Variables:**
   ```env
   BASE_URL=https://downlodr.com
   CORS_ORIGINS=https://downlodr.com,https://www.downlodr.com,https://your-app-url.leapcell.io
   ```

---

## 🔧 **TECHNICAL DETAILS**

### **What Was Fixed:**

1. **Added Gunicorn** to `requirements.txt`:

   ```txt
   gunicorn>=21.0.0,<22.0.0
   ```

2. **Created WSGI Adapter** (`wsgi.py`):

   ```python
   from api.main import app
   application = app  # ASGI application
   ```

3. **Created Procfile** with proper FastAPI command:

   ```
   web: gunicorn -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080 --timeout 600 api.main:app
   ```

4. **Created Startup Script** (`start.sh`):
   ```bash
   #!/bin/bash
   exec gunicorn -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080 --timeout 600 api.main:app
   ```

### **Why This Works:**

- **FastAPI** is an ASGI application, not WSGI
- **Gunicorn** can run ASGI apps using `uvicorn.workers.UvicornWorker`
- **Port 8080** is what Leapcell.io expects
- **Proper import path** `api.main:app` points to our FastAPI app

---

## 🧪 **LOCAL TESTING**

Test the fixed configuration locally:

```bash
# Install gunicorn if not already installed
pip install gunicorn

# Test the same command Leapcell.io will use
gunicorn -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080 --timeout 600 api.main:app

# Test in another terminal
curl http://localhost:8080/
```

---

## 🎉 **EXPECTED RESULT**

After redeployment, you should see:

```bash
✅ Build successful
✅ Deployment successful
✅ Application running on port 8080
✅ API endpoints responding
✅ Ready for custom domain setup
```

---

## 🔍 **TROUBLESHOOTING**

### **If still getting errors:**

1. **Check Logs** in Leapcell.io dashboard
2. **Verify Environment Variables** are set correctly
3. **Test Import** locally:
   ```bash
   python -c "from api.main import app; print('OK')"
   ```

### **Common Issues:**

- **Import errors**: Check `PYTHONPATH` is set to `/app`
- **Port issues**: Ensure using port 8080 for Leapcell.io
- **Dependencies**: Verify all requirements in `requirements.txt`

---

## 📋 **DEPLOYMENT CHECKLIST**

- [x] ✅ Added `gunicorn` to requirements.txt
- [x] ✅ Created `wsgi.py` ASGI adapter
- [x] ✅ Created `Procfile` with correct command
- [x] ✅ Created `start.sh` startup script
- [x] ✅ Created `leapcell.yaml` configuration
- [ ] 🔄 Redeploy to Leapcell.io
- [ ] 🔄 Set environment variables
- [ ] 🔄 Test deployed endpoints
- [ ] 🔄 Add custom domain `downlodr.com`
- [ ] 🔄 Update DNS records
- [ ] 🔄 Test final URLs: `downlodr.com/abc123`

---

## 🎯 **NEXT STEPS**

1. **Redeploy** your app to Leapcell.io (should work now!)
2. **Test** the deployed endpoints
3. **Add custom domain** downlodr.com
4. **Update environment variables** with production URLs
5. **Test final result**: `downlodr.com/abc123` redirects

You're almost there! The fixes should resolve the deployment issue. 🚀
