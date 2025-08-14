import asyncio
import time
from typing import Optional
import logging
from requests import Response
from datetime import datetime
from repo_radar.config import GITHUB_DEFAULT_RATE

class RateLimitManager:
    def __init__(self):
        self.remaining: Optional[int] = None
        self.reset_time: Optional[int] = None
        self._lock = asyncio.Lock()
        self._lock_owner: Optional[asyncio.Task] = None
        self._headers_updated: bool = False
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        if self._lock_owner == asyncio.current_task():
            self.logger.error("RateLimitManager is not reentrant")
            raise RuntimeError("RateLimitManager is not reentrant")
        
        await self._lock.acquire()
        self._headers_updated = False
        self._lock_owner = asyncio.current_task()
        
        if self.remaining and self.remaining <= 0:
            now = time.time()
            wait_time = max(0, (self.reset_time or now) - now)
            
            if wait_time > 0:
                reset_dt = datetime.utcfromtimestamp(self.reset_time).strftime("%Y-%m-%d %H:%M:%S")
                self.logger.warning(f"Rate limit hit, sleeping until {reset_dt} ({wait_time:.1f}s)")
                await asyncio.sleep(wait_time)
                self.remaining = GITHUB_DEFAULT_RATE
            
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._headers_updated == False:
            self.logger.error("Must call update_from_headers() before releasing the rate limit lock")
            raise RuntimeError("Must call update_from_headers() before releasing the rate limit lock")
            
        self._lock_owner = None
        self._lock.release()

    async def update_from_headers(self, response: Response):
        if self._lock_owner != asyncio.current_task():
            self.logger.error("update_from_headers must be called within the RateLimitManager task holding the lock")
            raise RuntimeError("update_from_headers must be called within the RateLimitManager task holding the lock")
            
        try:
            remaining = int(response.headers.get("X-RateLimit-Remaining"))
            reset = int(response.headers.get("X-RateLimit-Reset"))
            
            if self.reset_time is None or self.reset_time < reset:
                self.reset_time = reset
                self.remaining = remaining
            
            self._headers_updated = True
            
        except (ValueError, TypeError):
            self.logger.warning("Rate limit headers missing from response.")
            raise RuntimeError("Rate limit headers missing from response.")
