"""Core URL shortening logic - now with configurable storage backends"""

import secrets
import string
import base64
import json
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
import logging

from .models import ShortURL, ShortenRequest, ShortenResponse
from .config import get_config, TalisikConfig
from .storage import create_storage, AbstractStorage

logger = logging.getLogger(__name__)


class URLShortener:
    """Main URL shortener class - now with pluggable storage backends"""
    
    def __init__(self, base_url: Optional[str] = None, config: Optional[TalisikConfig] = None, storage: Optional[AbstractStorage] = None):
        """
        Initialize URLShortener with optional configuration
        
        Args:
            base_url: Base URL for generating short URLs (overrides config)
            config: Configuration object (auto-loaded from env if None)
            storage: Storage backend (auto-created from config if None)
        """
        # Load configuration
        self.config = config or get_config()
        
        # Set base URL
        self.base_url = (base_url or self.config.base_url).rstrip('/')
        
        # Initialize storage backend
        self.storage = storage or create_storage(self.config)
        
        logger.info(f"URLShortener initialized with {type(self.storage).__name__} storage backend")

    def _modify_downlodr_url(self, url: str, expires_at: Optional[datetime]) -> str:
        """
        Modify downlodr.com URLs to replace createdAt with expires_at in shareId
        
        Args:
            url: Original URL to potentially modify
            expires_at: Expiration datetime to use instead of createdAt
            
        Returns:
            Modified URL or original URL if not a downlodr.com share-video URL
        """
        try:
            # Check if this is a downlodr.com share-video URL
            if "downlodr.com/share-video/?shareId=" not in url:
                return url
            
            # If no expiration date, return original URL
            if not expires_at:
                return url
            
            # Extract shareId from URL
            share_id_start = url.find("shareId=") + 8
            encoded_share_id = url[share_id_start:]
            
            # Decode the shareId (base64 decode)
            try:
                decoded_payload = base64.b64decode(encoded_share_id).decode('utf-8')
                payload = json.loads(decoded_payload)
                
                # Replace createdAt with expires_at
                payload['expiresAt'] = expires_at.isoformat()
                
                # Re-encode the payload
                new_encoded_payload = base64.b64encode(
                    json.dumps({
                        "url": payload['url'],
                        "expiresAt": payload['expiresAt'],
                    }).encode('utf-8')
                ).decode('utf-8')
                
                # Reconstruct the URL
                modified_url = f"https://downlodr.com/share-video/?shareId={new_encoded_payload}"
                
                logger.debug(f"Modified downlodr URL: replaced createdAt with expires_at")
                return modified_url
                
            except (json.JSONDecodeError, base64.binascii.Error) as decode_error:
                logger.warning(f"Failed to decode shareId, using original URL: {decode_error}")
                return url
                
        except Exception as e:
            logger.error(f"Error modifying downlodr URL: {e}")
            return url
    
    def shorten(self, request: ShortenRequest) -> ShortenResponse:
        """
        Shorten a URL - now with persistent storage
        
        Following Kaizen: Enhanced with database persistence while keeping the same API
        """
        try:
            # Validate URL (basic validation to start)
            if not self._is_valid_url(request.url):
                return ShortenResponse.error_response("Invalid URL provided", original_url=request.url)
            
            # Calculate expiration date
            expires_at = None
            if request.expires_hours:
                expires_at = datetime.now(UTC) + timedelta(milliseconds=request.expires_hours)

            # Modify downlodr URLs if needed
            modified_url = self._modify_downlodr_url(request.url, expires_at)

            # Generate short code
            short_code = request.custom_code or self._generate_code()
            
            # Check for conflicts using storage backend
            if self.storage.exists(short_code):
                return ShortenResponse.error_response(f"Short code '{short_code}' already exists", original_url=request.url)
            
            # Create short URL object using modified URL
            short_url_obj = ShortURL(
                id=secrets.token_urlsafe(16),  # Will be overridden by Xata if using XataStorage
                original_url=modified_url,  # Use modified URL
                short_code=short_code,
                created_at=datetime.now(),
                expires_at=expires_at
            )
            
            # Store using storage backend
            self.storage.set(short_url_obj)
            logger.debug(f"Successfully shortened URL: {request.url} -> {short_code}")
            
            return ShortenResponse.success_response(
                short_url=f"{self.base_url}/{short_code}",
                original_url=modified_url,
                short_code=short_code,
                expires_at=expires_at
            )
            
        except Exception as e:
            error_msg = f"Failed to store shortened URL: {e}"
            logger.error(error_msg)
            return ShortenResponse.error_response(error_msg, original_url=request.url)
    
    def expand(self, short_code: str) -> Optional[str]:
        """
        Expand a short code back to original URL
        
        Enhanced with persistent storage and better error handling
        """

        try:
            short_url = self.storage.get(short_code)
            if not short_url:
                logger.debug(f"Short code not found: {short_code}")
                return None
                
            # Check if expired
            if short_url.expires_at and datetime.now(UTC) > short_url.expires_at:
                logger.debug(f"Short code expired: {short_code}")
                return None
            
            # Check if active
            if not short_url.is_active:
                logger.debug(f"Short code inactive: {short_code}")
                return None
            
            # Increment click count using storage backend
            new_count = self.storage.update_click_count(short_code)
            if new_count is not None:
                logger.debug(f"Updated click count for {short_code}: {new_count}")
            
            return short_url.original_url
            
        except Exception as e:
            logger.error(f"Error expanding short code {short_code}: {e}")
            return None
    
    def get_info(self, short_code: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a short URL without redirecting
        
        Enhanced with persistent storage access
        """
        try:
            url_obj = self.storage.get(short_code)
            if not url_obj:
                return None
            
            return {
                "short_code": short_code,
                "original_url": url_obj.original_url,
                "created_at": url_obj.created_at.isoformat(),
                "expires_at": url_obj.expires_at.isoformat() if url_obj.expires_at else None,
                "click_count": url_obj.click_count,
                "is_active": url_obj.is_active,
                "is_expired": url_obj.expires_at and datetime.now(UTC) > url_obj.expires_at if url_obj.expires_at else False
            }
            
        except Exception as e:
            logger.error(f"Error getting info for short code {short_code}: {e}")
            return None
    
    def stats(self) -> Dict[str, Any]:
        """
        Get basic statistics about all URLs
        
        Enhanced with persistent storage statistics
        """
        try:
            return self.storage.get_stats()
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"total_urls": 0, "active_urls": 0, "total_clicks": 0}
    
    def delete(self, short_code: str) -> bool:
        """
        Delete a short URL
        
        New functionality enabled by storage abstraction
        """ 
        try:
            result = self.storage.delete(short_code)
            if result:
                logger.debug(f"Successfully deleted short code: {short_code}")
            else:
                logger.debug(f"Short code not found for deletion: {short_code}")
            return result
        except Exception as e:
            logger.error(f"Error deleting short code {short_code}: {e}")
            return False
    
    def deactivate(self, short_code: str) -> bool:
        """
        Deactivate a short URL (soft delete)
        
        New functionality that preserves analytics
        """
        try:
            url_obj = self.storage.get(short_code)
            if not url_obj:
                return False
            
            url_obj.is_active = False
            self.storage.set(url_obj)  # Update the record
            logger.debug(f"Deactivated short code: {short_code}")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating short code {short_code}: {e}")
            return False
    
    def _generate_code(self, length: Optional[int] = None) -> str:
        """Generate a random short code using configured length"""
        code_length = length or self.config.default_code_length
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(code_length))
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation - will enhance incrementally"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about stored URLs
        
        Returns:
            Dict with total_urls, active_urls, total_clicks
        """
        return self.storage.get_stats()
    
    def get_all_urls(self) -> List[Dict[str, Any]]:
        """
        Get all shortened URLs for table display
        
        Returns:
            List of URL objects with selected fields for table
        """
        try:
            return self.storage.get_all_urls()
        except Exception as e:
            logger.error(f"Error getting all URLs: {e}")
            return [] 