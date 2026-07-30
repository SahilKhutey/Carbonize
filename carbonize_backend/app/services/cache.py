"""
Redis caching service with tiered TTL
"""
import redis.asyncio as redis
import pickle
import hashlib
import asyncio
from typing import Optional, Any, Callable, TypeVar
from functools import wraps
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self):
        self.pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=False,
        )
    
    async def get_redis(self) -> redis.Redis:
        return redis.Redis(connection_pool=self.pool)
    
    async def get(self, key: str) -> Optional[Any]:
        try:
            r = await self.get_redis()
            data = await r.get(key)
            if data is None:
                return None
            return pickle.loads(data)
        except Exception as e:
            logger.warning(f"Cache get failed for {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        try:
            r = await self.get_redis()
            ttl = ttl or settings.REDIS_CACHE_TTL
            await r.set(key, pickle.dumps(value), ex=ttl)
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        try:
            r = await self.get_redis()
            await r.delete(key)
            return True
        except Exception:
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        try:
            r = await self.get_redis()
            keys = []
            async for key in r.scan_iter(match=pattern, count=100):
                keys.append(key)
            if keys:
                return await r.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern failed: {e}")
            return 0


cache = CacheService()
