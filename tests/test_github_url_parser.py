import unittest
from repo_radar.utils.github_url_parser import extract_github_urls
from repo_radar.models.github_url import GithubUrl

class TestGitHubURLParser(unittest.TestCase):
    def test_valid_urls(self):
        test_input = """
        https://github.com/github/gitignore/blob/main/Python.gitignore
        https://github.com/REPO-RADAR/repo-radar/tree/6-create-github-url-parser
        git@github.com:octocat/Hello-World.git
        http://www.github.com/user123/my-repo
        https://github.com/user_with_underscore/repo-name123/
        """
        expected = [
            GithubUrl(full_url="https://github.com/github/gitignore/blob/main/Python.gitignore",
                      org_user="github",
                      repo="gitignore"),
            GithubUrl(full_url="https://github.com/REPO-RADAR/repo-radar/tree/6-create-github-url-parser",
                      org_user="REPO-RADAR",
                      repo="repo-radar"),
            GithubUrl(full_url="git@github.com:octocat/Hello-World.git",
                      org_user="octocat",
                      repo="Hello-World"),
            GithubUrl(full_url="http://www.github.com/user123/my-repo",
                      org_user="user123",
                      repo="my-repo"),
            GithubUrl(full_url="https://github.com/user_with_underscore/repo-name123/",
                      org_user="user_with_underscore",
                      repo="repo-name123"),
        ]
        result = extract_github_urls(test_input)
        self.assertEqual(result, expected)

    def test_invalid_urls(self):
        test_input = """
        https://gitlab.com/user/repo
        https://github.com/
        just some random text
        https://github.com//missingorg/repo
        """
        expected = []  # No valid GitHub repo URLs expected
        result = extract_github_urls(test_input)
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
