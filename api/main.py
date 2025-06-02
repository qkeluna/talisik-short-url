"""FastAPI application for Talisik URL Shortener"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional
import uvicorn

from talisik import URLShortener, ShortenRequest

# Initialize FastAPI app
app = FastAPI(
    title="Talisik URL Shortener API",
    description="Privacy-focused URL shortener inspired by tnyr.me",
    version="0.1.0",
)

# Initialize URL shortener (in production, this would use persistent storage)
shortener = URLShortener(base_url="http://localhost:8000")


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
    return {
        "total_urls": len(shortener._urls),
        "active_urls": sum(1 for url in shortener._urls.values() if url.is_active),
        "total_clicks": sum(url.click_count for url in shortener._urls.values())
    }

@app.get("/info/{short_code}")
async def get_url_info(short_code: str):
    """Get information about a short URL without redirecting"""
    if short_code not in shortener._urls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found"
        )
    
    url_obj = shortener._urls[short_code]
    
    return {
        "short_code": short_code,
        "original_url": url_obj.original_url,
        "created_at": url_obj.created_at.isoformat(),
        "expires_at": url_obj.expires_at.isoformat() if url_obj.expires_at else None,
        "click_count": url_obj.click_count,
        "is_active": url_obj.is_active
    }

@app.get("/{short_code}")
async def redirect_url(short_code: str):
    """Redirect to original URL (main shortener functionality)"""
    original_url = shortener.expand(short_code)
    
    if not original_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found or expired"
        )
    
    return RedirectResponse(url=original_url, status_code=status.HTTP_301_MOVED_PERMANENTLY)


# Development server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 