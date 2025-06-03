"""Storage backend implementations for Talisik Short URL service"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime, UTC
import logging
import uuid

from .models import ShortURL
from .config import TalisikConfig

logger = logging.getLogger(__name__)


class AbstractStorage(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    def get(self, short_code: str) -> Optional[ShortURL]:
        """Retrieve a ShortURL by its short code"""
        pass
    
    @abstractmethod
    def set(self, short_url: ShortURL) -> None:
        """Store a ShortURL"""
        pass
    
    @abstractmethod
    def delete(self, short_code: str) -> bool:
        """Delete a ShortURL by short code. Returns True if deleted, False if not found"""
        pass
    
    @abstractmethod
    def exists(self, short_code: str) -> bool:
        """Check if a short code already exists"""
        pass
    
    @abstractmethod
    def update_click_count(self, short_code: str) -> Optional[int]:
        """Increment click count for a short code. Returns new count or None if not found"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, int]:
        """Get basic statistics about stored URLs"""
        pass
    
    @abstractmethod
    def get_all_urls(self) -> List[Dict[str, Any]]:
        """Get all URLs for table display"""
        pass


class MemoryStorage(AbstractStorage):
    """In-memory storage implementation - good for development and testing"""
    
    def __init__(self):
        self._urls: Dict[str, ShortURL] = {}
        logger.info("Initialized MemoryStorage backend")
    
    def get(self, short_code: str) -> Optional[ShortURL]:
        return self._urls.get(short_code)
    
    def set(self, short_url: ShortURL) -> None:
        self._urls[short_url.short_code] = short_url
        logger.debug(f"Stored URL with short_code: {short_url.short_code}")
    
    def delete(self, short_code: str) -> bool:
        if short_code in self._urls:
            del self._urls[short_code]
            logger.debug(f"Deleted URL with short_code: {short_code}")
            return True
        return False
    
    def exists(self, short_code: str) -> bool:
        return short_code in self._urls
    
    def update_click_count(self, short_code: str) -> Optional[int]:
        if short_code in self._urls:
            self._urls[short_code].click_count += 1
            new_count = self._urls[short_code].click_count
            logger.debug(f"Updated click count for {short_code}: {new_count}")
            return new_count
        return None
    
    def get_stats(self) -> Dict[str, int]:
        return {
            "total_urls": len(self._urls),
            "active_urls": sum(1 for url in self._urls.values() if url.is_active),
            "total_clicks": sum(url.click_count for url in self._urls.values())
        }
    
    def get_all_urls(self) -> List[Dict[str, Any]]:
        """Get all URLs for table display with specified columns"""
        urls = []
        for url_obj in self._urls.values():
            urls.append({
                "original_url": url_obj.original_url,
                "short_code": url_obj.short_code,
                "expires_at": url_obj.expires_at.isoformat() if url_obj.expires_at else None,
                "click_count": url_obj.click_count,
                "is_active": url_obj.is_active,
                "created_at": url_obj.created_at.isoformat()
            })
        # Sort by created_at desc (newest first)
        return sorted(urls, key=lambda x: x["created_at"], reverse=True)


class XataStorage(AbstractStorage):
    """Xata.io storage implementation - production ready"""
    
    def __init__(self, config: TalisikConfig):
        self.config = config
        self._client = None
        self._table_name = "short_urls"
        logger.info(f"Initialized XataStorage backend for database: {config.xata_database_url}")
    
    @property
    def client(self):
        """Lazy initialization of Xata client"""
        if self._client is None:
            try:
                from xata import XataClient
                # Initialize with API key and database URL
                self._client = XataClient(
                    api_key=self.config.xata_api_key,
                    db_url=self.config.xata_database_url
                )
                logger.info("Xata client initialized successfully")
            except ImportError:
                raise ImportError("xata package not installed. Run: pip install xata")
            except Exception as e:
                logger.error(f"Failed to initialize Xata client: {e}")
                raise
        return self._client
    
    def get(self, short_code: str) -> Optional[ShortURL]:
        """Retrieve a ShortURL by its short code using SQL"""
        try:
            # Use SQL query - this works with manually created tables
            result = self.client.sql().query(
                "SELECT * FROM short_urls WHERE short_code = $1",
                [short_code]
            )
            
            if result and result.get('records') and len(result['records']) > 0:
                record = result['records'][0]
                return self._record_to_short_url(record)
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving URL with short_code {short_code}: {e}")
            return None
    
    def set(self, short_url: ShortURL) -> None:
        """Store a ShortURL in Xata using SQL with explicit xata_id"""
        try:
            # Generate explicit xata_id since Xata requires it
            xata_id = str(uuid.uuid4())
            
            # Provide explicit xata_id and all required fields
            if short_url.expires_at:
                sql = """
                    INSERT INTO short_urls (xata_id, original_url, short_code, expires_at, click_count, is_active)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING xata_id
                """
                params = [
                    xata_id,
                    short_url.original_url,
                    short_url.short_code,
                    short_url.expires_at.isoformat(),
                    short_url.click_count,
                    short_url.is_active
                ]
            else:
                sql = """
                    INSERT INTO short_urls (xata_id, original_url, short_code, click_count, is_active)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING xata_id
                """
                params = [
                    xata_id,
                    short_url.original_url,
                    short_url.short_code,
                    short_url.click_count,
                    short_url.is_active
                ]
            
            logger.debug(f"Inserting record with explicit xata_id: {sql}")
            logger.debug(f"Parameters: {params}")
            
            result = self.client.sql().query(sql, params)
            logger.debug(f"SQL Insert result: {result}")
            
            # Check if insert was successful
            if result and result.get('records') and len(result['records']) > 0:
                record = result['records'][0]
                if record.get('xata_id'):
                    short_url.id = record['xata_id']
                    logger.debug(f"Successfully stored URL with short_code: {short_url.short_code}, xata_id: {record['xata_id']}")
                else:
                    logger.warning(f"Insert succeeded but no xata_id returned: {result}")
            else:
                logger.error(f"SQL Insert failed: {result}")
                raise Exception(f"SQL Insert failed: {result}")
                
        except Exception as e:
            logger.error(f"Error storing URL with short_code {short_url.short_code}: {e}")
            raise
    
    def delete(self, short_code: str) -> bool:
        """Delete a ShortURL by short code using SQL"""
        try:
            # Use SQL DELETE - this works with manually created tables
            result = self.client.sql().query(
                "DELETE FROM short_urls WHERE short_code = $1 RETURNING xata_id",
                [short_code]
            )
            
            if result and result.get('records') and len(result['records']) > 0:
                logger.debug(f"Successfully deleted URL with short_code: {short_code}")
                return True
            else:
                logger.debug(f"No URL found to delete with short_code: {short_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting URL with short_code {short_code}: {e}")
            return False
    
    def exists(self, short_code: str) -> bool:
        """Check if a short code already exists"""
        return self.get(short_code) is not None
    
    def update_click_count(self, short_code: str) -> Optional[int]:
        """Increment click count for a short code using SQL"""
        try:
            # Use SQL UPDATE - this works with manually created tables
            result = self.client.sql().query(
                "UPDATE short_urls SET click_count = click_count + 1 WHERE short_code = $1 RETURNING click_count",
                [short_code]
            )
            
            if result and result.get('records') and len(result['records']) > 0:
                new_count = result['records'][0]['click_count']
                logger.debug(f"Updated click count for {short_code}: {new_count}")
                return new_count
            else:
                logger.debug(f"No URL found to update click count for short_code: {short_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error updating click count for {short_code}: {e}")
            return None
    
    def get_stats(self) -> Dict[str, int]:
        """Get basic statistics about stored URLs using SQL"""
        try:
            # Use SQL to get stats - this works with manually created tables
            result = self.client.sql().query(
                "SELECT COUNT(*) as total_urls, SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active_urls, SUM(click_count) as total_clicks FROM short_urls"
            )
            
            if result and result.get("records") and len(result["records"]) > 0:
                stats = result["records"][0]
                return {
                    "total_urls": int(stats.get("total_urls", 0)),
                    "active_urls": int(stats.get("active_urls", 0)),
                    "total_clicks": int(stats.get("total_clicks", 0))
                }
            
            return {"total_urls": 0, "active_urls": 0, "total_clicks": 0}
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"total_urls": 0, "active_urls": 0, "total_clicks": 0}
    
    def get_all_urls(self) -> List[Dict[str, Any]]:
        """Get all URLs for table display with specified columns"""
        try:
            # Use SQL to get all URLs with only the required columns
            result = self.client.sql().query(
                "SELECT original_url, short_code, expires_at, click_count, is_active, created_at FROM short_urls ORDER BY created_at DESC"
            )
            
            if result and result.get("records"):
                urls = []
                for record in result["records"]:
                    urls.append({
                        "original_url": record["original_url"],
                        "short_code": record["short_code"],
                        "expires_at": record["expires_at"],
                        "click_count": record.get("click_count", 0),
                        "is_active": record.get("is_active", True),
                        "created_at": record["created_at"]
                    })
                return urls
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting all URLs: {e}")
            return []
    
    def _record_to_short_url(self, record: Dict) -> ShortURL:
        """Convert SQL query result to ShortURL object"""
        # SQL queries return records with 'xata_id' field
        record_id = record.get("xata_id", record.get("id", ""))
        
        return ShortURL(
            id=record_id,
            original_url=record["original_url"],
            short_code=record["short_code"],
            created_at=datetime.fromisoformat(record["created_at"].replace("Z", "+00:00")),
            expires_at=datetime.fromisoformat(record["expires_at"].replace("Z", "+00:00")) if record.get("expires_at") else None,
            click_count=record.get("click_count", 0),
            is_active=record.get("is_active", True)
        )
    
    def _short_url_to_record(self, short_url: ShortURL) -> Dict:
        """Convert ShortURL object to Xata record"""
        record = {
            "original_url": short_url.original_url,
            "short_code": short_url.short_code,
            "created_at": short_url.created_at.isoformat(),
            "click_count": short_url.click_count,
            "is_active": short_url.is_active
        }
        
        if short_url.expires_at:
            record["expires_at"] = short_url.expires_at.isoformat()
        
        return record


def create_storage(config: TalisikConfig) -> AbstractStorage:
    """Factory function to create storage backend based on configuration"""
    if config.storage_backend == "xata":
        return XataStorage(config)
    elif config.storage_backend == "memory":
        return MemoryStorage()
    else:
        raise ValueError(f"Unknown storage backend: {config.storage_backend}") 