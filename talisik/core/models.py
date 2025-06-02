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
    expires_at: Optional[datetime] = None 