"""FastAPI application for Talisik URL Shortener"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional
import uvicorn

from talisik.core.shortener import URLShortener
from talisik.core.models import ShortenRequest

# Initialize FastAPI app
app = FastAPI(
    title="Talisik URL Shortener API",
    description="Privacy-focused URL shortener inspired by tnyr.me",
    version="0.1.0",
)

import os

# Initialize URL shortener (in production, this would use persistent storage)
base_url = os.getenv("BASE_URL", "http://localhost:8000")
shortener = URLShortener(base_url=base_url)


# Pydantic models for API
class ShortenUrlRequest(BaseModel):
    url: HttpUrl
    custom_code: Optional[str] = None
    expires_hours: Optional[int] = None

class ShortenUrlResponse(BaseModel):
    short_url: str
    original_url: str
    short_code: str
    expires_at: Optional[str] = None


# API Endpoints
@app.get("/")
async def root():
    """API root - basic info"""
    return {
        "service": "Talisik URL Shortener",
        "version": "0.1.0",
        "endpoints": {
            "shorten": "POST /shorten",
            "expand": "GET /{short_code}",
            "info": "GET /info/{short_code}",
            "stats": "GET /api/stats",
            "docs": "GET /docs"
        }
    }

@app.post("/shorten", response_model=ShortenUrlResponse)
async def shorten_url(request: ShortenUrlRequest):
    """Shorten a URL"""
    try:
        # Convert FastAPI model to library model
        lib_request = ShortenRequest(
            url=str(request.url),
            custom_code=request.custom_code,
            expires_hours=request.expires_hours
        )
        
        # Use our library to shorten
        result = shortener.shorten(lib_request)
        
        return ShortenUrlResponse(
            short_url=result.short_url,
            original_url=result.original_url,
            short_code=result.short_code,
            expires_at=result.expires_at.isoformat() if result.expires_at else None
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.get("/api/stats")
async def get_stats():
    """Get basic statistics"""
    return shortener.stats()

@app.get("/info/{short_code}")
async def get_url_info(short_code: str):
    """Get information about a short URL without redirecting"""
    info = shortener.get_info(short_code)
    
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found"
        )
    
    return info

@app.get("/{short_code}")
async def redirect_url(short_code: str):
    """Redirect to original URL (main shortener functionality)"""
    original_url = shortener.expand(short_code)
    
    if not original_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found or expired"
        )
    
    # Basic URL validation to prevent open redirects
    from urllib.parse import urlparse
    parsed = urlparse(original_url)
    if not parsed.scheme or not parsed.netloc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid destination URL"
        )
    
    return RedirectResponse(url=original_url, status_code=status.HTTP_301_MOVED_PERMANENTLY)


# Development server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 