"""Tests for URL shortener functionality"""

import pytest
from datetime import datetime, timedelta, UTC

from talisik.core.shortener import URLShortener
from talisik.core.models import ShortenRequest


class TestURLShortener:
    """Test suite for URLShortener class"""

    def setup_method(self):
        """Set up fresh URLShortener for each test"""
        self.shortener = URLShortener(base_url="http://test.com")

    def test_shorten_valid_url(self):
        """Test shortening a valid URL"""
        request = ShortenRequest(url="https://example.com")
        result = self.shortener.shorten(request)
        
        assert result.short_url.startswith("http://test.com/")
        assert result.original_url == "https://example.com"
        assert len(result.short_code) == 7  # Default length
        assert result.expires_at is None

    def test_shorten_invalid_url(self):
        """Test that invalid URLs raise an error"""
        request = ShortenRequest(url="not-a-url")
        
        with pytest.raises(ValueError, match="Invalid URL provided"):
            self.shortener.shorten(request)

    def test_expand_existing_code(self):
        """Test expanding an existing short code"""
        # First shorten a URL
        request = ShortenRequest(url="https://example.com")
        result = self.shortener.shorten(request)
        
        # Then expand it
        expanded = self.shortener.expand(result.short_code)
        assert expanded == "https://example.com"

    def test_expand_nonexistent_code(self):
        """Test expanding a code that doesn't exist"""
        result = self.shortener.expand("nonexistent")
        assert result is None

    def test_custom_short_code(self):
        """Test using a custom short code"""
        request = ShortenRequest(url="https://example.com", custom_code="custom123")
        result = self.shortener.shorten(request)
        
        assert result.short_code == "custom123"
        assert result.short_url == "http://test.com/custom123"

    def test_duplicate_custom_code_fails(self):
        """Test that duplicate custom codes fail"""
        # Create first URL with custom code
        request1 = ShortenRequest(url="https://example.com", custom_code="duplicate")
        self.shortener.shorten(request1)
        
        # Try to create second URL with same custom code
        request2 = ShortenRequest(url="https://other.com", custom_code="duplicate")
        
        with pytest.raises(ValueError, match="Short code 'duplicate' already exists"):
            self.shortener.shorten(request2)

    def test_url_expiration(self):
        """Test URL expiration functionality"""
        # Create URL that expires in 24 hours
        request = ShortenRequest(url="https://example.com", expires_hours=24)
        result = self.shortener.shorten(request)
        
        # Should work immediately
        expanded = self.shortener.expand(result.short_code)
        assert expanded == "https://example.com"
        
        # Check expiration is set
        assert result.expires_at is not None
        
        # Manually expire by setting expires_at to past
        short_url_obj = self.shortener._urls[result.short_code]
        short_url_obj.expires_at = datetime.now(UTC) - timedelta(hours=1)
        
        # Should return None when expired
        expanded = self.shortener.expand(result.short_code)
        assert expanded is None

    def test_get_info_existing_code(self):
        """Test getting info for an existing short code"""
        # First shorten a URL
        request = ShortenRequest(url="https://example.com", custom_code="info123")
        result = self.shortener.shorten(request)
        
        # Get info
        info = self.shortener.get_info("info123")
        
        assert info is not None
        assert info["short_code"] == "info123"
        assert info["original_url"] == "https://example.com"
        assert info["click_count"] == 0
        assert info["is_active"] is True
        assert info["is_expired"] is False
        assert "created_at" in info
        assert "expires_at" in info

    def test_get_info_nonexistent_code(self):
        """Test getting info for a code that doesn't exist"""
        info = self.shortener.get_info("nonexistent")
        assert info is None

    def test_get_info_expired_url(self):
        """Test getting info for an expired URL"""
        # Create URL with expiration
        request = ShortenRequest(url="https://example.com", expires_hours=1)
        result = self.shortener.shorten(request)
        
        # Manually expire by setting expires_at to past
        short_url_obj = self.shortener._urls[result.short_code]
        short_url_obj.expires_at = datetime.now(UTC) - timedelta(hours=1)
        
        # Get info - should still return info but show expired
        info = self.shortener.get_info(result.short_code)
        
        assert info is not None
        assert info["is_expired"] is True

    def test_stats_empty(self):
        """Test stats with no URLs"""
        stats = self.shortener.stats()
        
        assert stats["total_urls"] == 0
        assert stats["active_urls"] == 0
        assert stats["total_clicks"] == 0

    def test_stats_with_urls(self):
        """Test stats with multiple URLs"""
        # Create a few URLs
        self.shortener.shorten(ShortenRequest(url="https://example1.com"))
        self.shortener.shorten(ShortenRequest(url="https://example2.com"))
        self.shortener.shorten(ShortenRequest(url="https://example3.com"))
        
        # Expand one to increment click count
        codes = list(self.shortener._urls.keys())
        self.shortener.expand(codes[0])
        self.shortener.expand(codes[0])  # Click twice
        
        stats = self.shortener.stats()
        
        assert stats["total_urls"] == 3
        assert stats["active_urls"] == 3
        assert stats["total_clicks"] == 2 