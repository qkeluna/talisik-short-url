"""FastAPI application for Talisik URL Shortener"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional
import uvicorn
import os

from talisik.core.shortener import URLShortener
from talisik.core.models import ShortenRequest

# Initialize FastAPI app
app = FastAPI(
    title="Talisik URL Shortener API",
    description="Privacy-focused URL shortener inspired by tnyr.me",
    version="0.1.0",
)

# Dynamic CORS configuration for custom domain support
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],  # Support downlodr.com
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize URL shortener with dynamic base URL (supports custom domain)
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
        
        # Check if the operation was successful
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error or "Failed to shorten URL"
            )
        
        return ShortenUrlResponse(
            short_url=result.short_url,
            original_url=result.original_url,
            short_code=result.short_code,
            expires_at=result.expires_at.isoformat() if result.expires_at else None
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/stats")
async def get_stats():
    """Get basic statistics"""
    return shortener.get_stats()

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

@app.head("/{short_code}")
async def head_redirect_url(short_code: str):
    """HEAD request for redirect (returns redirect headers without body for client SDK expand method)"""
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