import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from core.config import settings

class TokenBucket:
    def __init__(self, rate: int, burst: int):
        self.rate = rate
        self.capacity = burst
        self.tokens = burst
        self.timestamp = time.monotonic()

    def allow(self) -> bool:
        now = time.monotonic()
        elapsed = now - self.timestamp
        self.timestamp = now
        self.tokens = min(self.capacity, self.tokens + elapsed * (self.rate/60))
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

class RateLimitMiddleware(BaseHTTPMiddleware):
    buckets: dict[str, TokenBucket] = {}

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "anon"
        bucket = self.buckets.setdefault(ip, TokenBucket(settings.rate_limit_per_min, settings.rate_limit_burst))
        if not bucket.allow():
            raise HTTPException(status_code=429, detail="Too Many Requests")