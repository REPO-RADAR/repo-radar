import requests
from requests.exceptions import HTTPError
from repo_radar.config import GITHUB_API_USER_ENDPOINT, GITHUB_DEFAULT_PAGE, GITHUB_MAX_PAGINATED
from repo_radar.models.github_token import GitHubToken
from repo_radar.models.github_url import GithubUrl

def validate_github_token(token: GitHubToken):
    """
    Calls /user endpoint of provided GitHub token and throws exception if request fails.
    
    Args:
        token (GitHubToken): GitHub Token Dataclass Object
        
    Raises:
        requests.exceptions.HTTPError: If token is invalid or request fails.
    """
    response = requests.get(f"{GITHUB_API_USER_ENDPOINT}", headers=token.to_header())
    try:
        response.raise_for_status()
    except HTTPError as err:
        if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":    # If we get an exception and it's a rate limit, then the token is valid.
            return response.json()
        raise err
    return response

def get_repo_languages(token: GitHubToken, url: GithubUrl) -> dict:
    """
    Fetch the languages used in a GitHub repository.
    
    Args:
        token (GitHubToken): GitHub Token Dataclass Object
        url (GithubUrl): GitHub URL Dataclass Object
    
    Returns:
        dict: A dictionary of languages and their byte size in the repo
    
    Raises:
        requests.exceptions.HTTPError: If token is invalid or request fails.
    """
    response = requests.get(url.api_languages_path(), headers=token.to_header())
    response.raise_for_status()
    return response

def get_license(token: GitHubToken, url: GithubUrl):
    """
    Fetch the licenses used in a GitHub repository.
    
    Args:
        token (GitHubToken): GitHub Token Dataclass Object
        url (GithubUrl): GitHub URL Dataclass Object
    
    Raises:
        requests.exceptions.HTTPError: If token is invalid or request fails.
    """
    response = requests.get(url.api_license_path(), headers=token.to_header())
    response.raise_for_status()
    return response

def get_paginated_url(token: GitHubToken, url: str, page: int = GITHUB_DEFAULT_PAGE, per_page: int = GITHUB_MAX_PAGINATED):
    """
    Perform a single-page GET request to the GitHub API.

    Args:
        url (str): Full API endpoint URL.
        token (GitHubToken): GitHub token dataclass.
        page (int): Page number to request.
        per_page (int): Items per page (max 100).
        
    Raises:
        ValueError: If page per_page < 1 or per_page exceeds 100

    Returns:
        tuple: (list|dict JSON response, requests.Response object)
    """
    
    if page < 1:
        raise ValueError("Page number must be >= 1")
    if not (1 <= per_page <= GITHUB_MAX_PAGINATED):
        raise ValueError(f"per_page must be between 1 and {GITHUB_MAX_PAGINATED}")
    
    params = {
        "page": page,
        "per_page": per_page
    }
    response = requests.get(url, headers=token.to_header(), params=params)
    response.raise_for_status()
    return response

def get_contributors(token: GitHubToken, url: GithubUrl, page: int = GITHUB_DEFAULT_PAGE, per_page: int = GITHUB_MAX_PAGINATED):
    """
    Get a single page of contributors for a repository.
    
    args:
        url (GithubUrl): GithubUrl dataclass representing a repo url
        token (GitHubToken): GitHub token dataclass.
        page (int): Page number to request.
        per_page (int): Items per page (max 100).
    """
    return get_paginated_url(token, url.api_contributors_path(), page, per_page)

def get_issues(token: GitHubToken, url: GithubUrl, page: int = GITHUB_DEFAULT_PAGE, per_page: int = GITHUB_MAX_PAGINATED):
    """
    Get a single page of issues for a repository.
    
    args:
        url (GithubUrl): GithubUrl dataclass representing a repo url
        token (GitHubToken): GitHub token dataclass.
        page (int): Page number to request.
        per_page (int): Items per page (max 100).
    """
    return get_paginated_url(token, url.api_issues_path(), page, per_page)

def get_commits(token: GitHubToken, url: GithubUrl, page: int = GITHUB_DEFAULT_PAGE, per_page: int = GITHUB_MAX_PAGINATED):
    """
    Get a single page of commits for a repository.
    
    args:
        url (GithubUrl): GithubUrl dataclass representing a repo url
        token (GitHubToken): GitHub token dataclass.
        page (int): Page number to request.
        per_page (int): Items per page (max 100).
    """
    return get_paginated_url(token, url.api_commits_path(), page, per_page)

def get_pulls(token: GitHubToken, url: GithubUrl, page: int = GITHUB_DEFAULT_PAGE, per_page: int = GITHUB_MAX_PAGINATED):
    """
    Get a single page of pulls for a repository.
    
    args:
        url (GithubUrl): GithubUrl dataclass representing a repo url
        token (GitHubToken): GitHub token dataclass.
        page (int): Page number to request.
        per_page (int): Items per page (max 100).
    """
    return get_paginated_url(token, url.api_pulls_path(), page, per_page)