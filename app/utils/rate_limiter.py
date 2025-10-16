import time
import redis
from fastapi import HTTPException
from app.core.config import REDIS_URL

r = redis.Redis.from_url(REDIS_URL)

def check_rate_limit(tenant_id: str, limit: int = 30, window: int = 60):
    """Simple Redis-based fixed window rate limiter."""
    key = f"ratelimit:{tenant_id}:{int(time.time() // window)}"
    current = r.incr(key)
    if current == 1:
        r.expire(key, window)
    if current > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded for this tenant")
