#!/bin/bash
# Startup script for Talisik Short URL on Leapcell.io

# Set environment variables for production
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1

# Option 1: Run with gunicorn + uvicorn workers (recommended for production)
exec gunicorn -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080 --timeout 600 api.main:app

# Option 2: Run with uvicorn directly (alternative)
# exec uvicorn api.main:app --host 0.0.0.0 --port 8080 