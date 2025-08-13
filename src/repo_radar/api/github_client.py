from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from repo_radar.models.github_token import GitHubToken
from repo_radar.models.github_url import GithubUrl
from repo_radar.config import GITHUB_MAX_PAGINATED, MAX_RETRIES
import repo_radar.api.github_api as github_api
from repo_radar.utils.rate_limit_manager import RateLimitManager
import asyncio
from requests import Response
import logging

class AbstractGitHubApiClient(ABC):
    def __init__(self, passed_token: str):
        self.token = GitHubToken(passed_token)
        github_api.validate_github_token(self.token)

    @abstractmethod
    async def get_languages(self, url: GithubUrl) -> Response:
        """Return languages."""
        pass

    @abstractmethod
    async def get_license(self, url: GithubUrl) -> Response:
        """Return license information."""
        pass

    @abstractmethod
    async def get_commits(self, url: GithubUrl) -> List[Response]:
        """Return all commits."""
        pass

    @abstractmethod
    async def get_issues(self, url: GithubUrl) -> List[Response]:
        """Return all issues."""
        pass

    @abstractmethod
    async def get_pulls(self, url: GithubUrl) -> List[Response]:
        """Return all pull requests."""
        pass

    @abstractmethod
    async def get_contributors(self, url: GithubUrl) -> List[Response]:
        """Return all contributors."""
        pass

class GitHubClient(AbstractGitHubApiClient):
    def __init__(self, passed_token: str):
        super().__init__(passed_token)
        self.rate_manager = RateLimitManager()
        self.logger = logging.getLogger(__name__)
        
    async def _get_github_page(self, url: str) -> Response:
        async with self.rate_manager:
            response = await asyncio.to_thread(github_api.get_github_url, self.token, url)
            await self.rate_manager.update_from_headers(response)
            
        return response
        
    async def _get_paginated_github_page(self, url: str) -> Tuple[Response, Optional[str]]:
        async with self.rate_manager:
            response, next_url = await asyncio.to_thread(github_api.paginate_github_url, self.token, url=url, per_page=GITHUB_MAX_PAGINATED)
            await self.rate_manager.update_from_headers(response)
            
        return response, next_url
    
    async def _paginate_github_url(self, url:str) -> List[Response]:
        responses = []
        response, next_url = await self._get_paginated_github_page(url)
        responses.append(response)
        
        while next_url is not None:
            retries = 0
            while True:
                try:
                    response, next_url = await self._get_paginated_github_page(next_url)
                    responses.append(response)
                    break
                except Exception as e:
                    if retries < MAX_RETRIES:
                        retries += 1
                        self.logger.warning("Unexpected error while paginating GitHub url. Retrying...")
                        await asyncio.sleep(1) # Backoff
                        continue
                    self.logger.error(f"Retried {retries} times on {next_url}. Raising error.")
                    raise e
        
        return responses
    
    async def get_languages(self, url: GithubUrl) -> Response:
        return await self._get_github_page(url.api_languages_path())

    async def get_license(self, url: GithubUrl) -> Response:
        return await self._get_github_page(url.api_license_path())

    async def get_commits(self, url: GithubUrl) -> List[Response]:
        return await self._paginate_github_url(url.api_commits_path())

    async def get_issues(self, url: GithubUrl) -> List[Response]:
        return await self._paginate_github_url(url.api_issues_path())

    async def get_pulls(self, url: GithubUrl) -> List[Response]:
        return await self._paginate_github_url(url.api_pulls_path())

    async def get_contributors(self, url: GithubUrl) -> List[Response]:
        return await self._paginate_github_url(url.api_contributors_path())
