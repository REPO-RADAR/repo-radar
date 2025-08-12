from abc import ABC, abstractmethod
from typing import Any
from repo_radar.models.github_token import GitHubToken
from repo_radar.models.github_url import GithubUrl
from repo_radar.config import GITHUB_DEFAULT_PAGE, GITHUB_MAX_PAGINATED
import repo_radar.api.github_api as github_api
from repo_radar.utils.rate_limit_manager import RateLimitManager
from repo_radar.utils.github_parsers import paginated_has_next
import asyncio

class AbstractGitHubApiClient(ABC):
    def __init__(self, passed_token: str):
        self.token = GitHubToken(passed_token)
        github_api.validate_github_token(self.token)
    
    # --- Protected single-page async fetch methods for paginated endpoints ---
    @abstractmethod
    async def _get_commits_page(self, url: GithubUrl, page: int = GITHUB_DEFAULT_PAGE, per_page: int = GITHUB_MAX_PAGINATED) -> Any:
        """Fetch a single page of commits."""
        pass

    @abstractmethod
    async def _get_issues_page(self, url: GithubUrl, page: int = GITHUB_DEFAULT_PAGE, per_page: int = GITHUB_MAX_PAGINATED) -> Any:
        """Fetch a single page of issues."""
        pass

    @abstractmethod
    async def _get_pulls_page(self, url: GithubUrl, page: int = GITHUB_DEFAULT_PAGE, per_page: int = GITHUB_MAX_PAGINATED) -> Any:
        """Fetch a single page of pull requests."""
        pass

    @abstractmethod
    async def _get_contributors_page(self, url: GithubUrl, page: int = GITHUB_DEFAULT_PAGE, per_page: int = GITHUB_MAX_PAGINATED) -> Any:
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
        self.rate_manager = RateLimitManager()

    async def _get_commits_page(self, url: GithubUrl, page: int = GITHUB_DEFAULT_PAGE, per_page: int = GITHUB_MAX_PAGINATED) -> Any:
        async with self.rate_manager:
            response = await asyncio.to_thread(github_api.get_commits, self.token, url, page, per_page)
            await self.rate_manager.update_from_headers(response)
            return response

    async def _get_issues_page(self, url: GithubUrl, page: int = GITHUB_DEFAULT_PAGE, per_page: int = GITHUB_MAX_PAGINATED) -> Any:
        async with self.rate_manager:
            response = await asyncio.to_thread(github_api.get_issues, self.token, url, page, per_page)
            await self.rate_manager.update_from_headers(response)
            return response

    async def _get_pulls_page(self, url: GithubUrl, page: int = GITHUB_DEFAULT_PAGE, per_page: int = GITHUB_MAX_PAGINATED) -> Any:
        async with self.rate_manager:
            response = await asyncio.to_thread(github_api.get_pulls, self.token, url, page, per_page)
            await self.rate_manager.update_from_headers(response)
            return response

    async def _get_contributors_page(self, url: GithubUrl, page: int = GITHUB_DEFAULT_PAGE, per_page: int = GITHUB_MAX_PAGINATED) -> Any:
        async with self.rate_manager:
            response = await asyncio.to_thread(github_api.get_contributors, self.token, url, page, per_page)
            await self.rate_manager.update_from_headers(response)
            return response

    async def get_languages(self, url: GithubUrl) -> Any:
        async with self.rate_manager:
            response = await asyncio.to_thread(github_api.get_repo_languages, self.token, url)
            await self.rate_manager.update_from_headers(response)
            return response

    async def get_license(self, url: GithubUrl) -> Any:
        async with self.rate_manager:
            response = await asyncio.to_thread(github_api.get_license, self.token, url)
            await self.rate_manager.update_from_headers(response)
            return response

    async def get_commits(self, url: GithubUrl) -> Any:
        pass

    async def get_issues(self, url: GithubUrl) -> Any:
        pass

    async def get_pulls(self, url: GithubUrl) -> Any:
        pass

    async def get_contributors(self, url: GithubUrl) -> Any:
        contributors = []
        response = await self._get_contributors_page(url)
        contributors.append(response)
        page = 1
        while (paginated_has_next(response)):
            page += 1
            response = await self._get_contributors_page(url, page = page)
            contributors.append(response)
        
        return contributors
        
