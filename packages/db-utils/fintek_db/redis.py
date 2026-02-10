"""Redis utilities."""

import redis.asyncio as redis
from typing import Optional


_redis_client: Optional[redis.Redis] = None


async def get_redis_client(redis_url: str = "redis://localhost:6379") -> redis.Redis:
    """Get Redis client (singleton pattern)."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(redis_url, decode_responses=True)
    return _redis_client


async def close_redis_client():
    """Close Redis client."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
