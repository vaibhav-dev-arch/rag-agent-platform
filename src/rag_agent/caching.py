"""
Caching layer for RAG Agent Platform.
"""

import json
import hashlib
from typing import Optional, Any
from datetime import datetime, timedelta
import time

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

# In-memory cache fallback
_memory_cache: dict = {}
_cache_timestamps: dict = {}


class CacheManager:
    """Cache manager for RAG Agent Platform."""
    
    def __init__(self, redis_host: Optional[str] = None, redis_port: int = 6379, redis_db: int = 0):
        """Initialize cache manager."""
        self.redis_client = None
        self.cache_ttl = 3600  # 1 hour default
        
        if REDIS_AVAILABLE and redis_host:
            try:
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
            except Exception:
                self.redis_client = None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self.redis_client:
            try:
                cached = self.redis_client.get(key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass
        
        # Fallback to memory cache
        if key in _memory_cache:
            if key in _cache_timestamps:
                if time.time() - _cache_timestamps[key] < self.cache_ttl:
                    return _memory_cache[key]
                else:
                    # Expired
                    del _memory_cache[key]
                    del _cache_timestamps[key]
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        ttl = ttl or self.cache_ttl
        
        if self.redis_client:
            try:
                self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value)
                )
                return True
            except Exception:
                pass
        
        # Fallback to memory cache
        _memory_cache[key] = value
        _cache_timestamps[key] = time.time()
        return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
                return True
            except Exception:
                pass
        
        # Memory cache
        if key in _memory_cache:
            del _memory_cache[key]
            if key in _cache_timestamps:
                del _cache_timestamps[key]
            return True
        
        return False
    
    def clear(self, pattern: Optional[str] = None):
        """Clear cache entries."""
        if pattern:
            # Clear matching keys
            if self.redis_client:
                try:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                except Exception:
                    pass
            
            # Memory cache
            keys_to_delete = [k for k in _memory_cache.keys() if pattern in k]
            for key in keys_to_delete:
                del _memory_cache[key]
                if key in _cache_timestamps:
                    del _cache_timestamps[key]
        else:
            # Clear all
            if self.redis_client:
                try:
                    self.redis_client.flushdb()
                except Exception:
                    pass
            
            _memory_cache.clear()
            _cache_timestamps.clear()


# Global cache manager
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        import os
        redis_host = os.getenv("REDIS_HOST")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_db = int(os.getenv("REDIS_DB", "0"))
        _cache_manager = CacheManager(redis_host, redis_port, redis_db)
    return _cache_manager


def cache_query_result(ttl: int = 3600):
    """Decorator to cache query results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()
            cache_key = cache_manager._generate_key(f"query:{func.__name__}", *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

