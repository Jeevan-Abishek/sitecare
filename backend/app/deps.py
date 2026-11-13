import time
from collections import defaultdict, deque
from typing import Deque

from fastapi import Depends, HTTPException, Request

from app.database import SessionLocal
from app.config import get_settings

settings = get_settings()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self._calls: dict[str, Deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = time.time()
        window_start = now - self.window
        calls = self._calls[key]
        while calls and calls[0] < window_start:
            calls.popleft()
        if len(calls) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
        calls.append(now)


rate_limiter = RateLimiter(settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_WINDOW)


def rate_limit(request: Request):
    forwarded = request.headers.get("x-forwarded-for")
    client = (forwarded.split(",")[0].strip() if forwarded else request.client.host) if request.client else "unknown"
    rate_limiter.check(client)
