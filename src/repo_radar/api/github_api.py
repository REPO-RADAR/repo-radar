import requests
from requests import Response
from requests.exceptions import HTTPError
from repo_radar.config import GITHUB_API_USER_ENDPOINT, GITHUB_MAX_PAGINATED
from repo_radar.models.github_token import GitHubToken
from repo_radar.utils.github_parsers import get_next_paginated_url
from typing import Optional, Tuple

def validate_github_token(token: GitHubToken) -> Response:
    """
    Calls /user endpoint of provided GitHub token and throws exception if request fails.
    
    Args:
        token (GitHubToken): GitHub Token Dataclass Object
        
    Raises:
        requests.exceptions.HTTPError: If token is invalid or request fails.
        
    Returns:
        requests.Response: The HTTP response object.
    """
    response = requests.get(f"{GITHUB_API_USER_ENDPOINT}", headers=token.to_header())
    try:
        response.raise_for_status()
    except HTTPError as err:
        if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":    # If we get an exception and it's a rate limit, then the token is valid.
            return response.json()
        raise err
    return response

def get_github_url(token: GitHubToken, url: str) -> Response:
    """
    Fetch from GitHub API url and return response.
    
    Args:
        token (GitHubToken): GitHub Token Dataclass Object
        url (str): string of GitHub api url to fetch
    
    Raises:
        requests.exceptions.HTTPError: If token is invalid or request fails.
    
    Returns:
        requests.Response: The HTTP response object.
    """
    response = requests.get(url, token.to_header())
    response.raise_for_status()
    return response

def paginate_github_url(token: GitHubToken, url: str, per_page: int = GITHUB_MAX_PAGINATED) -> Tuple[Response, Optional[str]]:
    """
    Fetch from GitHub API url and return response with the next page URL if any.
    
    Args:
        token (GitHubToken): GitHub Token Dataclass Object
        url (str): string of GitHub api url to fetch
        per_page (int): Items per page (max 100)
    
    Raises:
        requests.exceptions.HTTPError: If token is invalid or request fails.
        ValueError: If per_page < 1 or exceeds 100 
    
    Returns:
        tuple: (requests.Response, Optional[str])
            - response (requests.Response): The HTTP response object.
            - next_url (Optional[str]): URL of the next page, or None if there are no more pages.
    """
    if not (1 <= per_page <= GITHUB_MAX_PAGINATED):
        raise ValueError(f"per_page must be between 1 and {GITHUB_MAX_PAGINATED}")
    
    params = {
        "per_page": per_page
    }
    response = requests.get(url, headers=token.to_header(), params=params)
    response.raise_for_status()
    next_url = get_next_paginated_url(response)
    return response, next_url