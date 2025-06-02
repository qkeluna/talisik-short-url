"""Data models for URL shortening operations"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ShortURL:
    """Represents a shortened URL with metadata"""
    id: str
    original_url: str
    short_code: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    click_count: int = 0
    is_active: bool = True


@dataclass
class ShortenRequest:
    """Request model for URL shortening"""
    url: str
    custom_code: Optional[str] = None
    expires_hours: Optional[int] = None


@dataclass  
class ShortenResponse:
    """Response model for URL shortening"""
    short_url: str
    original_url: str
    short_code: str
    success: bool = True
    error: Optional[str] = None
    expires_at: Optional[datetime] = None

    @classmethod
    def success_response(cls, short_url: str, original_url: str, short_code: str, expires_at: Optional[datetime] = None) -> 'ShortenResponse':
        """Create a successful response"""
        return cls(
            short_url=short_url,
            original_url=original_url,
            short_code=short_code,
            success=True,
            error=None,
            expires_at=expires_at
        )
    
    @classmethod
    def error_response(cls, error: str, original_url: str = "", short_code: str = "", short_url: str = "") -> 'ShortenResponse':
        """Create an error response"""
        return cls(
            short_url=short_url,
            original_url=original_url,
            short_code=short_code,
            success=False,
            error=error,
            expires_at=None
        ) 