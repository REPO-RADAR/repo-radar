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

    # def test_get_languages(self):
    #     response = self.GitHub.get_languages(self.url)
        
    # def test_get_license(self):
    #     response = self.GitHub.get_license(self.url)
        
    # def test_get_contributors(self):
    #     response = self.GitHub.get_contributors(self.url)
        
    # def test_get_branches(self):
    #     response = self.GitHub.get_branches(self.url)
        
    # def test_get_commits(self):
    #     response = self.GitHub.get_commits(self.url)
        
    # def test_get_pulls(self):
    #     response = self.GitHub.get_pulls(self.url)
    
    # def test_get_issues(self):
    #     response = self.GitHub.get_issues(self.url)
        
    def test_get_repo(self):
        response = self.GitHub.get_repo(self.url)
        print(response.__repr__())


if __name__ == "__main__":
    unittest.main()
