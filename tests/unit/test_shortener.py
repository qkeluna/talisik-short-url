"""Unit tests for core shortening functionality"""

import pytest
from datetime import datetime, timedelta, UTC

from talisik import URLShortener, ShortenRequest


class TestURLShortener:
    """Test the core URL shortener functionality"""
    
    def setup_method(self):
        """Set up fresh shortener for each test"""
        self.shortener = URLShortener()
    
    def test_shorten_valid_url(self):
        """Test shortening a valid URL - our first test"""
        request = ShortenRequest(url="https://google.com")
        response = self.shortener.shorten(request)
        
        assert response.original_url == "https://google.com"
        assert response.short_code is not None
        assert len(response.short_code) == 7  # default length
        assert response.short_url.startswith("http://localhost:3000/")
    
    def test_shorten_invalid_url(self):
        """Test that invalid URLs are rejected"""
        request = ShortenRequest(url="not-a-url")
        
        with pytest.raises(ValueError, match="Invalid URL provided"):
            self.shortener.shorten(request)
    
    def test_expand_existing_code(self):
        """Test expanding an existing short code"""
        # First shorten a URL
        request = ShortenRequest(url="https://example.com")
        response = self.shortener.shorten(request)
        
        # Then expand it
        expanded = self.shortener.expand(response.short_code)
        assert expanded == "https://example.com"
    
    def test_expand_nonexistent_code(self):
        """Test expanding a code that doesn't exist"""
        result = self.shortener.expand("nonexistent")
        assert result is None
    
    def test_custom_short_code(self):
        """Test using a custom short code"""
        request = ShortenRequest(url="https://google.com", custom_code="google")
        response = self.shortener.shorten(request)
        
        assert response.short_code == "google"
        assert response.short_url == "http://localhost:3000/google"
    
    def test_duplicate_custom_code_fails(self):
        """Test that duplicate custom codes are rejected"""
        request1 = ShortenRequest(url="https://google.com", custom_code="test")
        request2 = ShortenRequest(url="https://example.com", custom_code="test")
        
        self.shortener.shorten(request1)
        
        with pytest.raises(ValueError, match="Short code 'test' already exists"):
            self.shortener.shorten(request2)
    
    def test_url_expiration(self):
        """Test that URLs expire correctly"""
        # Create a URL that expires in 1 hour
        request = ShortenRequest(url="https://example.com", expires_hours=1)
        response = self.shortener.shorten(request)
        
        # Should work before expiration
        expanded = self.shortener.expand(response.short_code)
        assert expanded == "https://example.com"
        
        # Manually set expiration to past (simulating time passage)
        self.shortener._urls[response.short_code].expires_at = datetime.now(UTC) - timedelta(hours=1)
        
        # Should return None after expiration
        expired_result = self.shortener.expand(response.short_code)
        assert expired_result is None 