"""Redis caching utility for fast data retrieval."""

import json
from typing import Any, Optional

import redis.asyncio as redis

from app.config import settings

# Initialize

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
async def get_cache(key: str) -> Optional[Any]:
    """Retrieve JSON data from Redis by key."""

    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None

async def set_cache(key: str, value: Any, expire_seconds: int = 300):
    """Save data to Redis with an expiration timer (default 5 minutes)."""

    await redis_client.setex(key, expire_seconds, json.dumps(value))
async def invalidate_cache(key: str):
    """Delete a key from Redis (used when data changes and we want fresh data)."""
    
    await redis_client.delete(key)