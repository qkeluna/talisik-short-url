"""Storage backend implementations for Talisik Short URL service"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime, UTC
import logging

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


class SupabaseStorage(AbstractStorage):
    """Supabase (Postgres) storage implementation - production ready"""

    def __init__(self, config: TalisikConfig):
        self.config = config
        self._pool = None
        logger.info(f"Initialized SupabaseStorage backend (schema={config.supabase_db_schema})")

    @property
    def pool(self):
        """Lazy initialization of the Postgres connection pool"""
        if self._pool is None:
            try:
                from psycopg2.pool import ThreadedConnectionPool
                self._pool = ThreadedConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dsn=self.config.supabase_db_url,
                )
                logger.info("Supabase connection pool initialized successfully")
            except ImportError:
                raise ImportError("psycopg2 package not installed. Run: pip install psycopg2-binary")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase connection pool: {e}")
                raise
        return self._pool

    @property
    def _table(self):
        """Schema-qualified identifier for the short_urls table.

        Queries schema-qualify explicitly rather than relying on a connection
        `search_path`, so the app role used only needs USAGE on this one
        schema and CRUD on this one table -- it never has to be granted (or
        default to) visibility into any other schema the DSN's role can see.
        """
        from psycopg2 import sql
        return sql.Identifier(self.config.supabase_db_schema, "short_urls")

    def _execute(self, query, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Run a query against the pool, returning rows as dicts"""
        from psycopg2.extras import RealDictCursor

        conn = self.pool.getconn()
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params or [])
                    if cur.description is None:
                        return []
                    return [dict(row) for row in cur.fetchall()]
        finally:
            self.pool.putconn(conn)

    def get(self, short_code: str) -> Optional[ShortURL]:
        """Retrieve a ShortURL by its short code"""
        from psycopg2 import sql
        try:
            rows = self._execute(
                sql.SQL("SELECT * FROM {table} WHERE short_code = %s").format(table=self._table),
                [short_code],
            )
            return self._record_to_short_url(rows[0]) if rows else None
        except Exception as e:
            logger.error(f"Error retrieving URL with short_code {short_code}: {e}")
            return None

    def set(self, short_url: ShortURL) -> None:
        """Store a ShortURL in Supabase; id and created_at are assigned by the database"""
        from psycopg2 import sql
        try:
            if short_url.expires_at:
                query = sql.SQL(
                    "INSERT INTO {table} (original_url, short_code, expires_at, click_count, is_active) "
                    "VALUES (%s, %s, %s, %s, %s) RETURNING id"
                ).format(table=self._table)
                params = [
                    short_url.original_url,
                    short_url.short_code,
                    short_url.expires_at,
                    short_url.click_count,
                    short_url.is_active,
                ]
            else:
                query = sql.SQL(
                    "INSERT INTO {table} (original_url, short_code, click_count, is_active) "
                    "VALUES (%s, %s, %s, %s) RETURNING id"
                ).format(table=self._table)
                params = [
                    short_url.original_url,
                    short_url.short_code,
                    short_url.click_count,
                    short_url.is_active,
                ]

            rows = self._execute(query, params)

            if rows and rows[0].get("id"):
                short_url.id = str(rows[0]["id"])
                logger.debug(f"Successfully stored URL with short_code: {short_url.short_code}, id: {short_url.id}")
            else:
                logger.error(f"SQL Insert failed: {rows}")
                raise Exception(f"SQL Insert failed: {rows}")

        except Exception as e:
            logger.error(f"Error storing URL with short_code {short_url.short_code}: {e}")
            raise

    def delete(self, short_code: str) -> bool:
        """Delete a ShortURL by short code"""
        from psycopg2 import sql
        try:
            rows = self._execute(
                sql.SQL("DELETE FROM {table} WHERE short_code = %s RETURNING id").format(table=self._table),
                [short_code],
            )
            if rows:
                logger.debug(f"Successfully deleted URL with short_code: {short_code}")
                return True
            logger.debug(f"No URL found to delete with short_code: {short_code}")
            return False
        except Exception as e:
            logger.error(f"Error deleting URL with short_code {short_code}: {e}")
            return False

    def exists(self, short_code: str) -> bool:
        """Check if a short code already exists"""
        return self.get(short_code) is not None

    def update_click_count(self, short_code: str) -> Optional[int]:
        """Increment click count for a short code"""
        from psycopg2 import sql
        try:
            rows = self._execute(
                sql.SQL(
                    "UPDATE {table} SET click_count = click_count + 1 WHERE short_code = %s RETURNING click_count"
                ).format(table=self._table),
                [short_code],
            )
            if rows:
                new_count = rows[0]["click_count"]
                logger.debug(f"Updated click count for {short_code}: {new_count}")
                return new_count
            logger.debug(f"No URL found to update click count for short_code: {short_code}")
            return None
        except Exception as e:
            logger.error(f"Error updating click count for {short_code}: {e}")
            return None

    def get_stats(self) -> Dict[str, int]:
        """Get basic statistics about stored URLs"""
        from psycopg2 import sql
        try:
            rows = self._execute(
                sql.SQL(
                    "SELECT COUNT(*) as total_urls, "
                    "SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active_urls, "
                    "SUM(click_count) as total_clicks FROM {table}"
                ).format(table=self._table)
            )
            if rows:
                stats = rows[0]
                return {
                    "total_urls": int(stats.get("total_urls") or 0),
                    "active_urls": int(stats.get("active_urls") or 0),
                    "total_clicks": int(stats.get("total_clicks") or 0),
                }
            return {"total_urls": 0, "active_urls": 0, "total_clicks": 0}
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"total_urls": 0, "active_urls": 0, "total_clicks": 0}

    def get_all_urls(self) -> List[Dict[str, Any]]:
        """Get all URLs for table display with specified columns"""
        from psycopg2 import sql
        try:
            return self._execute(
                sql.SQL(
                    "SELECT original_url, short_code, expires_at, click_count, is_active, created_at "
                    "FROM {table} ORDER BY created_at DESC"
                ).format(table=self._table)
            )
        except Exception as e:
            logger.error(f"Error getting all URLs: {e}")
            return []

    def _record_to_short_url(self, record: Dict) -> ShortURL:
        """Convert a Postgres query result row into a ShortURL object"""
        return ShortURL(
            id=str(record.get("id", "")),
            original_url=record["original_url"],
            short_code=record["short_code"],
            created_at=record["created_at"],
            expires_at=record.get("expires_at"),
            click_count=record.get("click_count", 0),
            is_active=record.get("is_active", True),
        )


def create_storage(config: TalisikConfig) -> AbstractStorage:
    """Factory function to create storage backend based on configuration"""
    if config.storage_backend == "supabase":
        return SupabaseStorage(config)
    elif config.storage_backend == "memory":
        return MemoryStorage()
    else:
        raise ValueError(f"Unknown storage backend: {config.storage_backend}")