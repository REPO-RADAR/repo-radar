import unittest
import repo_radar.config as config
from repo_radar.models.github_token import GitHubToken
from repo_radar.api.github_api import validate_github_token
from requests.exceptions import HTTPError

class TestGitHubAPI(unittest.TestCase):

    def setUp(self):
        token = config.GITHUB_TOKEN
        if not token:
            self.skipTest("GITHUB_TOKEN environment variable not set")
        self.github_token = GitHubToken(token)

    def test_token_validity(self):
        try:
            validate_github_token(self.github_token)
        except HTTPError:
            self.fail("validate_github_token raised HTTPError unexpectedly. GitHubToken environment variable may be invalid.")

    def test_invalid_token(self):
        invalid_token = GitHubToken("invalid_token_123")
        with self.assertRaises(HTTPError):
            validate_github_token(invalid_token)

if __name__ == "__main__":
    unittest.main()
