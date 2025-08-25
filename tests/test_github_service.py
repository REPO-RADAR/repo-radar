import unittest
import asyncio
import repo_radar.config as config
from repo_radar.services.github_service import GitHubService
from repo_radar.utils.github_parsers import extract_github_urls
import requests


class TestGitHubService(unittest.TestCase):

    def setUp(self):
        token = config.GITHUB_TOKEN
        if not token:
            self.skipTest("GITHUB_TOKEN environment variable not set")
        self.GitHub = GitHubService(token)
        self.url = extract_github_urls(
            "https://github.com/REPO-RADAR/repo-radar"
        ).pop(0)

    def test_get_languages(self):
        response = self.GitHub.get_languages(self.url)
        print(response)
        
    def test_get_license(self):
        response = self.GitHub.get_license(self.url)
        print(response)
        
    def test_get_contributors(self):
        response = self.GitHub.get_contributors(self.url)
        print(response)
        
    def test_get_branches(self):
        response = self.GitHub.get_branches(self.url)
        print(response.pop(0).json())
    
    def test_get_issues(self):
        response = self.GitHub.get_issues(self.url)
        print(response)


if __name__ == "__main__":
    unittest.main()
