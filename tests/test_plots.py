import unittest
import repo_radar.config as config
from repo_radar.services.github_service import GitHubService
from repo_radar.services.analytics_service import Plotter
from repo_radar.utils.github_parsers import extract_github_urls

class TestGitHubService(unittest.TestCase):

    def setUp(self):
        token = config.GITHUB_TOKEN
        if not token:
            self.skipTest("GITHUB_TOKEN environment variable not set")
        self.GitHub = GitHubService(token)
        self.url = extract_github_urls(
            "https://github.com/REPO-RADAR/repo-radar"
        ).pop(0)
        
    def test_plotter(self):
        response = self.GitHub.get_repo(self.url)
        self.assertIsNotNone(response, "GitHubService.get_repo() returned None")
        self.assertIsNotNone(response.default_branch_commits, "default_branch_commits is None")
        self.assertGreater(len(response.default_branch_commits), 0, "No commits were returned for the default branch")

        plotter = Plotter()
        
        plotter.issues_bar_graph(response.issues)
        plotter.pulls_bar_graph(response.pulls)
        plotter.commits_per_day(response.default_branch_commits)
        for branch in response.branches:
            plotter.commits_per_day(branch.commits)
            
        plotter.issues_lifetime_graph(response.issues)



if __name__ == "__main__":
    unittest.main()
