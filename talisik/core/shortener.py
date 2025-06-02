"""Core URL shortening logic - our first working function"""

import secrets
import string
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from .models import ShortURL, ShortenRequest, ShortenResponse


class URLShortener:
    """Main URL shortener class - starts simple, grows incrementally"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url.rstrip('/')
        # Start with in-memory storage - will become configurable later
        self._urls: dict[str, ShortURL] = {}
    
    def shorten(self, request: ShortenRequest) -> ShortenResponse:
        """
        Shorten a URL - our first core function
        
        Following Kaizen: Start simple, add complexity incrementally
        """
        # Validate URL (basic validation to start)
        if not self._is_valid_url(request.url):
            raise ValueError("Invalid URL provided")
        
        # Generate short code
        short_code = request.custom_code or self._generate_code()
        
        # Check for conflicts (simple check initially)
        if short_code in self._urls:
            raise ValueError(f"Short code '{short_code}' already exists")
        
        # Calculate expiration
        expires_at = None
        if request.expires_hours:
            expires_at = datetime.now(UTC) + timedelta(hours=request.expires_hours)
        
        # Create and store short URL
        short_url_obj = ShortURL(
            id=secrets.token_urlsafe(16),
            original_url=request.url,
            short_code=short_code,
            created_at=datetime.now(UTC),
            expires_at=expires_at
        )
        
        self._urls[short_code] = short_url_obj
        
        return ShortenResponse(
            short_url=f"{self.base_url}/{short_code}",
            original_url=request.url,
            short_code=short_code,
            expires_at=expires_at
        )
    
    def expand(self, short_code: str) -> Optional[str]:
        """
        Expand a short code back to original URL
        
        Second core function - keeps things simple
        """
        if short_code not in self._urls:
            return None
        
        short_url = self._urls[short_code]
        
        # Check if expired
        if short_url.expires_at and datetime.now(UTC) > short_url.expires_at:
            return None
        
        # Check if active
        if not short_url.is_active:
            return None
        
        # Increment click count (simple analytics)
        short_url.click_count += 1
        
        return short_url.original_url
    
    def get_info(self, short_code: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a short URL without redirecting
        
        Provides proper encapsulation and uniform expiration checking
        """
        if short_code not in self._urls:
            return None
        
        url_obj = self._urls[short_code]
        
        return {
            "short_code": short_code,
            "original_url": url_obj.original_url,
            "created_at": url_obj.created_at.isoformat(),
            "expires_at": url_obj.expires_at.isoformat() if url_obj.expires_at else None,
            "click_count": url_obj.click_count,
            "is_active": url_obj.is_active,
            "is_expired": url_obj.expires_at and datetime.now(UTC) > url_obj.expires_at if url_obj.expires_at else False
        }
    
    def stats(self) -> Dict[str, Any]:
        """
        Get basic statistics about all URLs
        
        Provides proper encapsulation for statistics access
        """
        return {
            "total_urls": len(self._urls),
            "active_urls": sum(1 for url in self._urls.values() if url.is_active),
            "total_clicks": sum(url.click_count for url in self._urls.values())
        }
    
    def _generate_code(self, length: int = 7) -> str:
        """Generate a random short code"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation - will enhance incrementally"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False 