import unittest
import nest_asyncio
import asyncio
import repo_radar.config as config
from repo_radar.api.github_client import GitHubClient
from repo_radar.utils.github_url_parser import extract_github_urls

nest_asyncio.apply()

class TestAsyncGithubClient(unittest.TestCase):

    def setUp(self):
        token = config.GITHUB_TOKEN
        if not token:
            self.skipTest("GITHUB_TOKEN environment variable not set")
        self.client = GitHubClient(token)
        self.url = extract_github_urls(
            "https://github.com/REPO-RADAR/repo-radar"
        ).pop(0)

    def test_get_languages(self):
        async def run_test():
            languages = await self.client.get_languages(self.url)
            self.assertIsInstance(languages.json(), dict)

        asyncio.get_event_loop().run_until_complete(run_test()) # Needed to run nested async test

if __name__ == "__main__":
    unittest.main()
