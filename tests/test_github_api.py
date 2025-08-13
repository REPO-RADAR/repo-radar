import unittest
import repo_radar.config as config
from repo_radar.models.github_token import GitHubToken
from repo_radar.utils.github_parsers import extract_github_urls
from repo_radar.api.github_api import validate_github_token, paginate_github_url, get_github_url
from requests.exceptions import HTTPError

class TestGitHubAPI(unittest.TestCase):

    def setUp(self):
        token = config.GITHUB_TOKEN
        if not token:
            self.skipTest("GITHUB_TOKEN environment variable not set")
        self.github_token = GitHubToken(token)
        self.url = extract_github_urls("https://github.com/REPO-RADAR/repo-radar").pop(0)

    def test_token_validity(self):
        try:
            validate_github_token(self.github_token)
        except HTTPError:
            self.fail("validate_github_token raised HTTPError unexpectedly. GitHubToken environment variable may be invalid.")

    def test_invalid_token(self):
        invalid_token = GitHubToken("invalid_token_123")
        with self.assertRaises(HTTPError):
            validate_github_token(invalid_token)
            
    def test_get_github_url(self):                                              # Test hits the live Github API, replace with mocks later
        response = get_github_url(self.github_token,self.url.api_languages_path())
        self.assertEqual(response.status_code, 200)
            
    def test_paginate_github_url(self):                                          # Test hits the live Github API, replace with mocks later
       response, next_url = paginate_github_url(self.github_token, self.url.api_commits_path(), per_page=100)    
       self.assertEqual(response.status_code, 200)
       
if __name__ == "__main__":
    unittest.main()
