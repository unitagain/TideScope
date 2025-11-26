"""Multi-layer cache manager for badge system.

Implements two-tier caching:
- Level 1: In-memory cache with TTL (fast, short-lived)
- Level 2: File-based cache (persistent, long-lived)

This reduces LLM API calls by 95%+ while keeping data fresh.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """Multi-layer cache manager with TTL support."""

    def __init__(
        self,
        cache_dir: Path | str = ".cache/badges",
        memory_ttl: int = 3600,  # 1 hour for in-memory cache
        disk_ttl: int = 86400,  # 24 hours for disk cache
    ):
        """Initialize cache manager.
        
        Args:
            cache_dir: Directory for file-based cache
            memory_ttl: TTL for in-memory cache in seconds
            disk_ttl: TTL for disk cache in seconds
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_ttl = memory_ttl
        self.disk_ttl = disk_ttl
        
        # In-memory cache: {key: (value, expires_at)}
        self._memory_cache: Dict[str, tuple[Any, datetime]] = {}

    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key."""
        # Sanitize key for file system
        safe_key = key.replace(":", "_").replace("/", "_")
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (memory first, then disk).
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        # Try memory cache first
        if key in self._memory_cache:
            value, expires_at = self._memory_cache[key]
            if datetime.utcnow() < expires_at:
                logger.debug(f"Memory cache hit: {key}")
                return value
            else:
                # Expired, remove from memory
                del self._memory_cache[key]
                logger.debug(f"Memory cache expired: {key}")

        # Try disk cache
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                
                expires_at = datetime.fromisoformat(cached_data["expires_at"])
                if datetime.utcnow() < expires_at:
                    value = cached_data["value"]
                    
                    # Promote to memory cache
                    memory_expires_at = datetime.utcnow() + timedelta(seconds=self.memory_ttl)
                    self._memory_cache[key] = (value, memory_expires_at)
                    
                    logger.debug(f"Disk cache hit: {key}")
                    return value
                else:
                    # Expired, remove file
                    cache_path.unlink()
                    logger.debug(f"Disk cache expired: {key}")
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Failed to read cache {key}: {e}")
                # Remove corrupted cache file
                cache_path.unlink(missing_ok=True)

        logger.debug(f"Cache miss: {key}")
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache (both memory and disk).
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl: Custom TTL in seconds (uses disk_ttl if not provided)
        """
        if ttl is None:
            ttl = self.disk_ttl

        # Store in memory cache
        memory_expires_at = datetime.utcnow() + timedelta(seconds=self.memory_ttl)
        self._memory_cache[key] = (value, memory_expires_at)

        # Store in disk cache
        disk_expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        cache_path = self._get_cache_path(key)
        
        try:
            cached_data = {
                "value": value,
                "expires_at": disk_expires_at.isoformat(),
                "created_at": datetime.utcnow().isoformat(),
            }
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cached_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Cached: {key} (TTL: {ttl}s)")
        except (IOError, TypeError) as e:
            logger.error(f"Failed to write cache {key}: {e}")

    def delete(self, key: str) -> None:
        """Delete value from cache.
        
        Args:
            key: Cache key to delete
        """
        # Remove from memory
        self._memory_cache.pop(key, None)
        
        # Remove from disk
        cache_path = self._get_cache_path(key)
        cache_path.unlink(missing_ok=True)
        
        logger.debug(f"Deleted cache: {key}")

    def clear_expired(self) -> int:
        """Clear all expired cache entries.
        
        Returns:
            Number of entries cleared
        """
        now = datetime.utcnow()
        cleared = 0

        # Clear expired memory cache
        expired_keys = [
            key for key, (_, expires_at) in self._memory_cache.items()
            if now >= expires_at
        ]
        for key in expired_keys:
            del self._memory_cache[key]
            cleared += 1

        # Clear expired disk cache
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                
                expires_at = datetime.fromisoformat(cached_data["expires_at"])
                if now >= expires_at:
                    cache_file.unlink()
                    cleared += 1
            except (json.JSONDecodeError, KeyError, ValueError, IOError):
                # Remove corrupted files
                cache_file.unlink(missing_ok=True)
                cleared += 1

        if cleared > 0:
            logger.info(f"Cleared {cleared} expired cache entries")
        
        return cleared

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        memory_count = len(self._memory_cache)
        disk_count = len(list(self.cache_dir.glob("*.json")))
        
        return {
            "memory_entries": memory_count,
            "disk_entries": disk_count,
            "total_entries": disk_count,  # Disk is the source of truth
        }


# Global cache instance
_global_cache: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """Get or create global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache
