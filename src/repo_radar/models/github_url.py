from dataclasses import dataclass
from repo_radar.config import GITHUB_API_URL
from datetime import datetime, timezone

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
    
    def api_repo_path(self) -> str:
        """Repository metadata (includes default_branch, visibility, etc)."""
        return f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}"
    
    def api_languages_path(self) -> str:
        """Return full API endpoint for repository languages."""
        return f"{GITHUB_API_URL}/repos/{self.repo_path()}/languages"
    
    def api_contributors_path(self) -> str:
        """Return full API endpoint for contributors."""
        return f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}/contributors"
    
    def api_issues_path(self, since: int = None) -> str:
        """Repository issues list (open + closed depending on params).
        
        Args:
            since (int, optional): Unix timestamp to filter commits. Defaults to None.
        """
        url =  f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}/issues"
        url = self._append_since_to_path(url, since)
        return url
    
    def api_license_path(self) -> str:
        """Repository license information."""
        return f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}/license"
    
    def api_commits_path(self, since: int = None) -> str:
        """
        Return the GitHub REST API path to get commits.
    
        Args:
            since (int, optional): Unix timestamp to filter commits. Defaults to None.
    
        Returns:
            str: Full API URL for fetching commits.
        """
        url = f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}/commits"
        url = self._append_since_to_path(url, since)
        return url
    
    def api_activity_path(self) -> str:
        """Repository weekly commit activity."""
        return f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}/stats/commit_activity"
    
    def api_pulls_path(self, since: int = None) -> str:
        """Repository pull requests list.
        
        Args:
            since (int, optional): Unix timestamp to filter commits. Defaults to None.
        """
        url =  f"{GITHUB_API_URL}/repos/{self.org_user}/{self.repo}/pulls?state=all"
        url = self._append_since_to_path(url, since)
        return url
    
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
       url = self._append_since_to_path(url, since)
       return url
   
    def _append_since_to_path(self, url: str, since: int):
        if since is None or since < 1:
            return url
        iso_time = datetime.fromtimestamp(since, tz=timezone.utc).isoformat()
        url += f"?since={iso_time}"
        return url
