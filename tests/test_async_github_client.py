import unittest
import nest_asyncio
import asyncio
import repo_radar.config as config
from repo_radar.api.github_client import GitHubClient
from repo_radar.utils.github_parsers import extract_github_urls
import requests

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

        asyncio.get_event_loop().run_until_complete(run_test())
        
    def test_get_contributors(self):
        async def run_test():
            contributors = await self.client.get_contributors(self.url)
    
            self.assertIsInstance(contributors[0], requests.Response)
            self.assertIsInstance(contributors[0].json(), list)
            first_contributor = contributors[0].json()[0]
            self.assertIsInstance(first_contributor, dict)
    
        asyncio.get_event_loop().run_until_complete(run_test())
        
    def test_get_issues(self):
        async def run_test():
            issues = await self.client.get_issues(self.url)

            self.assertIsInstance(issues[0], requests.Response)
            self.assertIsInstance(issues[0].json(), list)
            first_issue = issues[0].json()[0]
            self.assertIsInstance(first_issue, dict)
    
        asyncio.get_event_loop().run_until_complete(run_test())



if __name__ == "__main__":
    unittest.main()
