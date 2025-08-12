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
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        async with self._lock:
            if self.remaining is not None and self.remaining <= 0:
                now = time.time()
                wait_time = max(0, (self.reset_time or now) - now)
                
                if wait_time > 0:
                    reset_dt = datetime.utcfromtimestamp(self.reset_time).strftime("%Y-%m-%d %H:%M:%S")
                    self.logger.warning(f"Rate limit hit, sleeping until {reset_dt} ({wait_time:.1f}s)")
                    await asyncio.sleep(wait_time)
                    self.remaining = GITHUB_DEFAULT_RATE
                    
            if self.remaining is not None:
                self.remaining -= 1
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def update_from_headers(self, response: Response):
        async with self._lock:
            try:
                remaining = int(response.headers.get("X-RateLimit-Remaining"))
                reset = int(response.headers.get("X-RateLimit-Reset"))
                
                if self.reset_time is None or self.reset_time < reset:  # Headers may arrive out of sequence, only update if header is more recent.
                    self.reset_time = reset
                    self.remaining = remaining
    
            except (ValueError, TypeError):
                self.logger.warning("Rate limit headers missing from response.")
                response.raise_for_status()