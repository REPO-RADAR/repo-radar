import re
from requests import Response
from typing import List
from repo_radar.models.github_url import GithubUrl
from repo_radar.config import GITHUB_URL_REGEX, LINK_HEADER_NEXT_REGEX

def extract_github_urls(text: str) -> List[GithubUrl]:
    """
    Extracts GitHub repository URLs from the passed string.

    Parses the input text to find all GitHub URLs matching common URL patterns
    (https, ssh, with or without .git suffix), and returns a list of `GithubUrl` 
    dataclass instances containing the full URL, the organization/user, and the 
    repository name.

    Args:
        text (str): The input string which may contain one or more GitHub URLs.

    Returns:
        List[GithubUrl]: A list of `GithubUrl` objects representing each matched URL.
    """
    regex = re.compile(GITHUB_URL_REGEX)
    matches = regex.finditer(text)
    results = []

    for match in matches:
        full_url = match.group()
        org_user = match.group("org_user")
        repo = match.group("repo")
        results.append(GithubUrl(full_url=full_url, org_user=org_user, repo=repo))

    return results

def paginated_has_next(response: Response) -> bool:
    link_header = response.headers.get("Link", "")
    if not link_header:
        return False
    return bool(re.search(LINK_HEADER_NEXT_REGEX, link_header))

def get_next_paginated_url(response: Response) -> str:
    link_header = response.headers.get("Link", "")
    next_url = None
    if link_header:
        for part in link_header.split(","):
            section = part.split(";")
            if len(section) == 2 and 'rel="next"' in section[1]:
                next_url = section[0].strip()[1:-1]  # remove < >
                break
    return next_url