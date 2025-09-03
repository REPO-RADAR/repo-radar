import asyncio
import time
from typing import Optional
import logging
from requests import Response
from datetime import datetime, timezone
from repo_radar.config import GITHUB_DEFAULT_RATE

class RateLimitManager:
    """
    RateLimitManager async-compatible class

    Tracks API rate limits using state variables and updates them by parsing
    rate limit headers from an HTTP response.
    
    Users must use update_from_headers to update state variables before exiting.
    
    Can be initialised with an HTTP response to set initial limits, otherwise
    initialises with default values.
    
    Args:
        - response (Response): The optional HTTP Response object to be parsed

    Attributes:
        - remaining (Optional[int]): Remaining API requests allowed before reset.
        - reset_time (Optional[int]): Unix timestamp for the next rate limit reset.
        - _lock (asyncio.Lock): Synchronisation primitive for blocking tasks.
        - _lock_owner (Optional[asyncio.Task]): Current owner of the lock.
        - _headers_updated (bool): Whether headers were updated before exiting.
        - logger (logging.Logger): Logger instance for reporting and errors.
    """
    def __init__(self, initial_headers: Optional[Response] = None):
        self.remaining: Optional[int] = None
        self.reset_time: Optional[int] = None
        self._lock = asyncio.Lock()
        self._lock_owner: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(__name__)
        
        if initial_headers:
            if not self._set_limits_from_headers(initial_headers):
                self.logger.error("RateLimitManager continuing with default limits...")
                self._set_default_limits()
        else:
            self._set_default_limits()
            
        self._headers_updated: bool = False
          
    """
    Set rate limit values to default values
    """
    def _set_default_limits(self):
        self.remaining = GITHUB_DEFAULT_RATE
        self.reset_time = int(time.time()) + 3600
        
    """
    Parses Response link headers and updates limit variables.
    
    Args:
        - response (Response): The optional HTTP Response object to be parsed
    
    Raises:
        - ValueError, TypeError: If resposne contains missing or invalid headers
    """
    def _set_limits_from_headers(self, response: Response) -> bool:
        try:
            remaining = int(response.headers.get("X-RateLimit-Remaining"))
            reset_time = int(response.headers.get("X-RateLimit-Reset"))
    
            if self.reset_time is None or reset_time > self.reset_time:         # Set limits if reset_time has expired or not set
                self.reset_time = reset_time
                self.remaining = remaining
            
            elif reset_time == self.reset_time and remaining < self.remaining:  # Update remaining for current reset window if new value is worse than current value
                self.remaining = remaining

            print(f"remain: {self.remaining}")
            self._headers_updated = True
    
            return True
    
        except (ValueError, TypeError):
            self.logger.warning("Rate limit headers missing or invalid in response.")
            return False


    async def __aenter__(self):
        """
        Implements the __aenter asyncio interface for use with asyncio
        
        Acquires the lock, checks current state of rate_limiter and sleeps if
        necessary.
        
        Raises:
            - RuntimeError: If lock is acquired by same coroutine twice
        """
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
                reset_dt = datetime.fromtimestamp(self.reset_time, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                self.logger.info(f"Rate limit hit, sleeping until {reset_dt} ({wait_time:.1f}s)")
                await asyncio.sleep(wait_time)
                self.remaining = GITHUB_DEFAULT_RATE
            
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Implements the __aexit asyncio interface for use with asyncio.
        
        Checks if headers were updated before releasing the lock.
        
        Raises:
            - RuntimeError: If lock is released without updating state variables
        """
        if self._headers_updated == False:
            self.logger.error("Must call update_from_headers() before releasing the rate limit lock")
            raise RuntimeError("Must call update_from_headers() before releasing the rate limit lock")
            
        self._lock_owner = None
        self._lock.release()

    async def update_from_headers(self, response: Response):
        """
        Parses Response link headers and updates state variables.
        
        Args:
            - response (Response): The HTTP Response object to be parsed
        
        Raises:
            - RuntimeError: If function is called by task that isn't the lock owner
                          or Response is missing limit headers.
        """
        if self._lock_owner != asyncio.current_task():
            self.logger.error("update_from_headers must be called within the RateLimitManager task holding the lock")
            raise RuntimeError("update_from_headers must be called within the RateLimitManager task holding the lock")
            
        if not self._set_limits_from_headers(response):
            raise RuntimeError("Rate limit headers missing from response.")
