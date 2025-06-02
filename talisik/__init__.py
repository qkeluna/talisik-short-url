"""
Talisik Short URL - Privacy-focused URL shortener

A modular library for creating and managing short URLs with privacy-first design.
"""

__version__ = "0.1.0"
__author__ = "Talisik Team"

from .core.shortener import URLShortener
from .core.models import ShortURL, ShortenRequest, ShortenResponse

__all__ = [
    "URLShortener", 
    "ShortURL", 
    "ShortenRequest", 
    "ShortenResponse"
] 