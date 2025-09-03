import unittest
import asyncio
import repo_radar.config as config
from repo_radar.api.github_client import GitHubClient
from repo_radar.utils.github_parsers import extract_github_urls
import requests


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

        asyncio.run(run_test())
        
    def test_get_contributors(self):
        async def run_test():
            contributors = await self.client.get_contributors(self.url)
            self.assertIsInstance(contributors[0], requests.Response)
            self.assertIsInstance(contributors[0].json(), list)
            first_contributor = contributors[0].json()[0]
            self.assertIsInstance(first_contributor, dict)

        asyncio.run(run_test())
        
    def test_get_issues(self):
        async def run_test():
            issues = await self.client.get_issues(self.url)
            self.assertIsInstance(issues[0], requests.Response)
            self.assertIsInstance(issues[0].json(), list)
            first_issue = issues[0].json()[0]
            self.assertIsInstance(first_issue, dict)

        asyncio.run(run_test())
        
    def test_get_branches(self):
        async def run_test():
            branches = await self.client.get_branches(self.url)
            self.assertIsInstance(branches[0], requests.Response)
            self.assertIsInstance(branches[0].json(), list)
            first_branch = branches[0].json()[0]
            self.assertIsInstance(first_branch, dict)

        asyncio.run(run_test())
        
    def test_get_metadata(self):
        async def run_test():
            metadata = await self.client.get_repo_metadata(self.url)
            self.assertIsInstance(metadata, requests.Response)
            self.assertIsInstance(metadata.json(), dict)
            
        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
