"""Redis-based rate limiting dependency"""

import redis.asyncio as redis
from fastapi import HTTPException, Request, status

from app.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
class RateLimiter:
    """Dependency to limit requests per minute per IP address."""

    def __init__(self, requests: int, window_seconds: int = 60):
        self.requests = requests
        self.window_seconds = window_seconds

    async def __call__(self, request: Request):
        ip = request.client.host if request.client else "127.0.0.1"
        endpoint = request.url.path
        
        key = f"rate_limit:{ip}:{endpoint}"
        
        current = await redis_client.incr(key)
        
        if current == 1:
            await redis_client.expire(key, self.window_seconds)
            
        if current > self.requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests} requests per {self.window_seconds} seconds."
            )