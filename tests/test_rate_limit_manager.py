import unittest
from unittest.mock import MagicMock
from requests.models import Response
from repo_radar.utils.rate_limit_manager import RateLimitManager
import logging

class TestRateLimitManager(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.rate_limit_manager = RateLimitManager()
        logging.disable(logging.CRITICAL)

    async def test_not_updating_headers(self):
        with self.assertRaises(RuntimeError) as context:
            async with self.rate_limit_manager:
                pass
        self.assertIn("Must call update_from_headers() before releasing the rate limit lock", str(context.exception))

    async def test_update_from_headers_requires_lock(self):
        response = MagicMock(spec=Response)
        response.headers = {
            "X-RateLimit-Remaining": "10",
            "X-RateLimit-Reset": str(int(1e10))
        }
        with self.assertRaises(RuntimeError) as context:
            await self.rate_limit_manager.update_from_headers(response)
        self.assertIn("update_from_headers must be called within the RateLimitManager task holding the lock", str(context.exception))
        self.assertEqual(self.rate_limit_manager.remaining, None)
        self.assertEqual(self.rate_limit_manager.reset_time, None)
        self.assertFalse(self.rate_limit_manager._headers_updated)

    async def test_update_from_headers_and_release(self):
        response = MagicMock(spec=Response)
        response.headers = {
            "X-RateLimit-Remaining": "10",
            "X-RateLimit-Reset": str(int(1e10))
        }
        async with self.rate_limit_manager:
            await self.rate_limit_manager.update_from_headers(response)
            self.assertEqual(self.rate_limit_manager.remaining, 10)
            self.assertEqual(self.rate_limit_manager.reset_time, int(1e10))
            self.assertTrue(self.rate_limit_manager._headers_updated)

    async def test_reentry(self):
        response = MagicMock(spec=Response)
        response.headers = {
            "X-RateLimit-Remaining": "10",
            "X-RateLimit-Reset": str(int(1e10))
        }
        async def enter_twice():
            async with self.rate_limit_manager:
                await self.rate_limit_manager.update_from_headers(response)
                # Attempt to reenter while already holding the lock
                await self.rate_limit_manager.__aenter__()

        with self.assertRaises(RuntimeError) as context:
            await enter_twice()
        self.assertIn("RateLimitManager is not reentrant", str(context.exception))

if __name__ == "__main__":
    unittest.main()
