from abc import ABC, abstractmethod
from typing import Any
from repo_radar.models.github_token import GitHubToken
from repo_radar.models.github_url import GithubUrl
import repo_radar.api.github_api as github_api

class AbstractGitHubApiClient(ABC):
    def __init__(self, passed_token: str):
        self.token = GitHubToken(passed_token)
        github_api.validate_github_token(self.token)
    
    # --- Protected single-page async fetch methods for paginated endpoints ---
    @abstractmethod
    async def _get_commits_page(self, url: GithubUrl, page: int, per_page: int) -> Any:
        """Fetch a single page of commits."""
        pass

    @abstractmethod
    async def _get_issues_page(self, url: GithubUrl, page: int, per_page: int) -> Any:
        """Fetch a single page of issues."""
        pass

    @abstractmethod
    async def _get_pulls_page(self, url: GithubUrl, page: int, per_page: int) -> Any:
        """Fetch a single page of pull requests."""
        pass

    @abstractmethod
    async def _get_contributors_page(self, url: GithubUrl, page: int, per_page: int) -> Any:
        """Fetch a single page of contributors."""
        pass

    # -------------------------------------------------------------------------

    @abstractmethod
    async def get_languages(self, url: GithubUrl) -> Any:
        """Return languages."""
        pass

    @abstractmethod
    async def get_license(self, url: GithubUrl) -> Any:
        """Return license information."""
        pass

    @abstractmethod
    async def get_commits(self, url: GithubUrl) -> Any:
        """Return all commits."""
        pass

    @abstractmethod
    async def get_issues(self, url: GithubUrl) -> Any:
        """Return all issues."""
        pass

    @abstractmethod
    async def get_pulls(self, url: GithubUrl) -> Any:
        """Return all pull requests."""
        pass

    @abstractmethod
    async def get_contributors(self, url: GithubUrl) -> Any:
        """Return all contributors."""
        pass

class GitHubClient(AbstractGitHubApiClient):
    def __init__(self, passed_token: str):
        super().__init__(passed_token)

    async def _get_commits_page(self, url: GithubUrl, page: int, per_page: int) -> Any:
        pass

    async def _get_issues_page(self, url: GithubUrl, page: int, per_page: int) -> Any:
        pass

    async def _get_pulls_page(self, url: GithubUrl, page: int, per_page: int) -> Any:
        pass

    async def _get_contributors_page(self, url: GithubUrl, page: int, per_page: int) -> Any:
        pass

    async def get_languages(self, url: GithubUrl) -> Any:
        pass

    async def get_license(self, url: GithubUrl) -> Any:
        pass

    async def get_commits(self, url: GithubUrl) -> Any:
        pass

    async def get_issues(self, url: GithubUrl) -> Any:
        pass

    async def get_pulls(self, url: GithubUrl) -> Any:
        pass

    async def get_contributors(self, url: GithubUrl) -> Any:
        pass
