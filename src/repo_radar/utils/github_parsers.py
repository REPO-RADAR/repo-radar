import re
from requests import Response
from typing import List
from repo_radar.models.github_url import GitHubUrl
from repo_radar.config import GITHUB_URL_REGEX, LINK_HEADER_NEXT_REGEX

def extract_github_urls(text: str) -> List[GitHubUrl]:
    """
    Extracts GitHub repository URLs from the passed string.

    Parses the input text to find all GitHub URLs matching common URL patterns
    (https, ssh, with or without .git suffix), and returns a list of `GitHubUrl` 
    dataclass instances containing the full URL, the organization/user, and the 
    repository name.

    Args:
        - text (str): The input string which may contain one or more GitHub URLs.

    Returns:
        - List[GitHubUrl]: A list of `GitHubUrl` objects representing each matched URL.
    """
    regex = re.compile(GITHUB_URL_REGEX)
    matches = regex.finditer(text)
    results = []

    for match in matches:
        full_url = match.group()
        org_user = match.group("org_user")
        repo = match.group("repo")
        results.append(GitHubUrl(full_url=full_url, org_user=org_user, repo=repo))

    return results

def paginated_has_next(response: Response) -> bool:
    """
    Check if a paginated GitHub API response has a 'next' page.

    Inspects the `Link` header of the HTTP response to determine whether
    there is a `rel="next"` entry indicating another page of results.

    Args:
        - response (Response): The HTTP response object from a GitHub API request.

    Returns:
        - bool: True if a next page exists, False otherwise.
    """
    link_header = response.headers.get("Link", "")
    if not link_header:
        return False
    return bool(re.search(LINK_HEADER_NEXT_REGEX, link_header))


def get_next_paginated_url(response: Response) -> str:
    """
    Extract the URL for the next page from a paginated GitHub API response.

    Parses the `Link` header of the HTTP response to find the `rel="next"`
    link, which points to the next page of results.

    Args:
        - response (Response): The HTTP response object from a GitHub API request.

    Returns:
        - str: The URL for the next page, or None if there is no next page.
    """
    link_header = response.headers.get("Link", "")
    next_url = None
    if link_header:
        for part in link_header.split(","):
            section = part.split(";")
            if len(section) == 2 and 'rel="next"' in section[1]:
                next_url = section[0].strip()[1:-1]  # remove < >
                break
    return next_url
