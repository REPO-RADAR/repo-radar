from dataclasses import dataclass
from repo_radar.config import GITHUB_API_URL

@dataclass
class GitHubUrl:
    """
    Represents a GitHub repository and provides API endpoint builders.

    Stores repository details and generates full API endpoint URLs for common
    GitHub resources such as languages, contributors, issues, commits, pull
    requests, and repository contents.

    Attributes:
        - full_url (str): The full HTTPS URL of the repository.
        - org_user (str): The GitHub organization or username that owns the repository.
        - repo (str): The repository name.
    """
    full_url: str
    org_user: str
    repo: str

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"<{class_name} org_user='{self.org_user}' repo='{self.repo}'>"
    
    def repo_path(self) -> str:
        """Return 'org_user/repo' string."""
        return f"{self.org_user}/{self.repo}"
    
    def api_languages_path(self) -> str:
        """Return full API endpoint for repository languages."""
        return f"{GITHUB_API_URL}/repos/{self.repo_path()}/languages"
    
    def api_contributors_path(self) -> str:
        """Return full API endpoint for contributors."""
        return f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}/contributors"
    
    def api_issues_path(self) -> str:
        """Repository issues list (open + closed depending on params)."""
        return f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}/issues"
    
    def api_license_path(self) -> str:
        """Repository license information."""
        return f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}/license"
    
    def api_commits_path(self) -> str:
        """Repository commits list."""
        return f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}/commits"
    
    def api_activity_path(self) -> str:
        """Repository weekly commit activity."""
        return f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}/stats/commit_activity"
    
    def api_pulls_path(self) -> str:
        """Repository pull requests list."""
        return f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}/pulls"
    
    def api_contents_path(self, path: str = "") -> str:
        """
        Repository contents list.
        
        Args:
            - path (str): Path for subdirectories or specific files. E.G: path="requirements.txt" or path="src"

        """
        if path:
            return f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}/contents/{path}"
        return f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}/contents"
    
    def api_branch_path(self) -> str:
        """Return the GitHub REST API path to list branches of the repository."""
        return f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}/branches"
    
    def api_compare_path(self, sha: str, since: int = None) -> str:
       """
       Return the GitHub REST API path to compare the main branch with another branch or commit.

       Args:
           - sha (str): SHA of the target branch or commit to compare with main.
           - since (int, optional): Unix timestamp to filter commits. Defaults to None.

       Returns:
           - str: Full API URL for comparing branches.
       """
       url = f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}/compare/main...{sha}"
       if since:
           url += f"?since={since}"
       return url
