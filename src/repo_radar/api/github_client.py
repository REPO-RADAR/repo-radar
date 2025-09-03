from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from repo_radar.models.github_token import GitHubToken
from repo_radar.models.github_url import GitHubUrl
from repo_radar.config import GITHUB_MAX_PAGINATED, MAX_RETRIES
import repo_radar.api.github_api as github_api
from repo_radar.utils.rate_limit_manager import RateLimitManager
import asyncio
from requests import Response
from requests.exceptions import HTTPError
import logging
import time

class AbstractGitHubApiClient(ABC):
    """
    Abstract base class for GitHub API clients.

    Defines the interface for asynchronous GitHub API operations such as
    retrieving repository languages, license, commits, issues, pull requests,
    and contributors. Implementations must provide concrete methods that
    adhere to these signatures.

    Args:
        - token (str): GitHub personal access token used for authentication.
    """

    def __init__(self, token: str):
        self.token = GitHubToken(token)

    @abstractmethod
    async def get_languages(self, url: GitHubUrl) -> Response:
        """Return languages."""
        pass

    @abstractmethod
    async def get_license(self, url: GitHubUrl) -> Response:
        """Return license information."""
        pass

    @abstractmethod
    async def get_commits(self, url: GitHubUrl) -> List[Response]:
        """Return all commits."""
        pass

    @abstractmethod
    async def get_issues(self, url: GitHubUrl) -> List[Response]:
        """Return all issues."""
        pass

    @abstractmethod
    async def get_pulls(self, url: GitHubUrl) -> List[Response]:
        """Return all pull requests."""
        pass

    @abstractmethod
    async def get_contributors(self, url: GitHubUrl) -> List[Response]:
        """Return all contributors."""
        pass
    
    @abstractmethod
    async def get_branches(self, url: GitHubUrl) -> List[Response]:
        """Return all branches"""
        pass
    
    @abstractmethod
    async def compare_branch(self, url: GitHubUrl, sha: str, delta: int) -> List[Response]:
        """Return commit difference between main branch and local branch up to maximum delta (days)"""
        pass

class GitHubClient(AbstractGitHubApiClient):
    """
    Async client for interacting with the GitHub API.

    Provides methods for fetching repository data such as languages, license,
    commits, issues, pull requests, and contributors. Automatically handles
    API rate limits.
    
    Attributes:
        - token (str): GitHub personal access token for authentication.
        - rate_manager (RateLimitManager): An async-compatible class for tracking API rate limit
        - logger (logging.Logger): Logger instance for reporting and errors.
    """

    def __init__(self, token: str):
        """Initialize the GitHub client.

        Args:
            - token (str): GitHub personal access token for authentication.
        """
        super().__init__(token)
        response = github_api.validate_github_token(self.token) # Validate the GitHub token and set the rate limits
        self.rate_manager = RateLimitManager(response)
        self.logger = logging.getLogger(__name__)

    async def _get_github_page(self, url: str) -> Response:
        """
        Fetch a single GitHub API page.

        Acquires the rate limit lock, sends the request, updates rate limit
        headers, and raises any HTTP errors.

        Args:
            - url (str): Full GitHub API URL to request.
        Returns:
            - Response: The HTTP response object.
        Raises:
            - HTTPError: If the response status is an error.
        """
        async with self.rate_manager:
            response = await asyncio.to_thread(github_api.get_github_url, self.token, url)
            await self.rate_manager.update_from_headers(response)
            response.raise_for_status()
        return response

    async def _get_paginated_github_page(self, url: str) -> Tuple[Response, Optional[str]]:
        """
        Fetch a single page of paginated GitHub API results.

        Acquires the rate limit lock, sends the request, updates rate limit
        headers, and returns both the response and the next page's URL.

        Args:
            - url (str): GitHub API URL for the current page.
        Returns:
            - Tuple[Response, Optional[str]]: The HTTP response and the URL for the next page, or None if there is no next page.
        Raises:
            - HTTPError: If the response status is an error.
        """
        async with self.rate_manager:
            response, next_url = await asyncio.to_thread(
                github_api.paginate_github_url,
                self.token,
                url=url,
                per_page=GITHUB_MAX_PAGINATED
            )
            await self.rate_manager.update_from_headers(response)
            response.raise_for_status()
        return response, next_url

    async def _paginate_github_url(self, url: str) -> List[Response]:
        """
        Fetch all pages of a paginated GitHub API endpoint.

        Automatically retries up to MAX_RETRIES times if a 403 rate limit error
        occurs, gives up if rate_limite_manager is unable to rectify after max
        retries.

        Args:
            - url (str): GitHub API URL to paginate through.
        Returns:
            - List[Response]: A list of HTTP responses, one per page.
        Raises:
            - HTTPError: If a non-retriable error occurs or retries are exhausted.
        """
        responses = []
        response, next_url = await self._get_paginated_github_page(url)
        responses.append(response)

        while next_url:
            retries = 0
            while True:
                try:
                    response, next_url = await self._get_paginated_github_page(next_url)
                    responses.append(response)
                    break
                except HTTPError as e:
                    status = getattr(e.response, "status_code", None)
                    if retries < MAX_RETRIES and status == 403:
                        retries += 1
                        self.logger.warning(
                            "HTTP Error 403 while paginating GitHub URL. Retrying..."
                        )
                        await asyncio.sleep(1)  # Backoff
                        continue
                    if status == 403:
                        self.logger.error(
                            f"Retried {retries} times on {next_url}. Raising error."
                        )
                        raise e
                    raise
        return responses

    async def get_languages(self, url: GitHubUrl) -> Response:
        """
        Get the programming languages used in a repository.

        Args:
            - url (GitHubUrl): Repository URL wrapper.
        Returns:
            - Response: The HTTP response containing languages data.
        """
        return await self._get_github_page(url.api_languages_path())

    async def get_license(self, url: GitHubUrl) -> Response:
        """
        Get the license information of a repository.

        Args:
            - url (GitHubUrl): Repository URL wrapper.
        Returns:
            - Response: The HTTP response containing license data.
        """
        return await self._get_github_page(url.api_license_path())

    async def get_commits(self, url: GitHubUrl, delta: int = 0) -> List[Response]:
        """
        Get the commit history of a repository's main branch

        Args:
            - url (GitHubUrl): Repository URL wrapper.
            - delta (int): Maximum number of days in the past to include commits.
        Returns:
            - List[Response]: List of HTTP responses containing commit data.
        """
        if delta > 0:
            since_timestamp = int(time.time()) - delta * 86400  # convert days to seconds
            commit_path = url.api_commits_path(since_timestamp)
        else:
            commit_path = url.api_commits_path()
        return await self._paginate_github_url(commit_path)

    async def get_issues(self, url: GitHubUrl, delta = 0) -> List[Response]:
        """
        Get the issues of a repository.

        Args:
            - url (GitHubUrl): Repository URL wrapper.
            - delta (int): Maximum number of days in the past to include commits.
        Returns:
            - List[Response]: List of HTTP responses containing issue data.
        """
        if delta > 0:
            since_timestamp = int(time.time()) - delta * 86400  # convert days to seconds
            issues_path = url.api_issues_path(since_timestamp)
        else:
            issues_path = url.api_issues_path(delta)
        return await self._paginate_github_url(issues_path)

    async def get_pulls(self, url: GitHubUrl, delta = 0) -> List[Response]:
        """
        Get the pull requests of a repository.

        Args:
            - url (GitHubUrl): Repository URL wrapper.
            - delta (int): Maximum number of days in the past to include commits.
        Returns:
            - List[Response]: List of HTTP responses containing pull request data.
        """
        if delta > 0:
            since_timestamp = int(time.time()) - delta * 86400  # convert days to seconds
            pulls_path = url.api_pulls_path(since_timestamp)
        else:
            pulls_path = url.api_pulls_path(delta)
        return await self._paginate_github_url(pulls_path)

    async def get_contributors(self, url: GitHubUrl) -> List[Response]:
        """
        Get the contributors of a repository.

        Args:
            - url (GitHubUrl): Repository URL wrapper.
        Returns:
            - List[Response]: List of HTTP responses containing contributor data.
        """
        return await self._paginate_github_url(url.api_contributors_path())
    
    async def get_branches(self, url: GitHubUrl) -> List[Response]:
        """
        Get the branches of a repository.

        Args:
            - url (GitHubUrl): Repository URL wrapper.
        Returns:
            - List[Response]: List of HTTP responses containing contributor data.
        """
        return await self._paginate_github_url(url.api_branch_path())

    async def compare_branch(self, url: GitHubUrl, sha: str, delta: int = 0) -> List[Response]:
        """
        Return commit difference between main branch and a given sha up to maximum delta (days).
    
        Args:
            - url (GitHubUrl): Repository URL wrapper.
            - sha (str): SHA of the branch or commit to compare.
            - delta (int): Maximum number of days in the past to include commits.
        Returns:
            - List[Response]: List of HTTP responses from GitHub containing commit data.
        """
        if delta > 0:
            since_timestamp = int(time.time()) - delta * 86400  # convert days to seconds
            compare_path = url.api_compare_path(sha, since_timestamp)
        else:
            compare_path = url.api_compare_path(sha)
        return await self._paginate_github_url(compare_path)
    
    async def get_repo_metadata(self, url: GitHubUrl) -> Response:
        """
        Get the meta data of a repository

        Args:
            - url (GitHubUrl): Repository URL wrapper.
        Returns:
            - Response: The HTTP response object.
        """
        return await self._get_github_page(url.api_repo_path())