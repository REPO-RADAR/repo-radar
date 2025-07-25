import re
from typing import List
from repo_radar.models.github_url import GithubUrl
from repo_radar.config import GITHUB_URL_REGEX

regex = re.compile(GITHUB_URL_REGEX)

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
    matches = regex.finditer(text)
    results = []

    for match in matches:
        full_url = match.group()
        org_user = match.group("org_user")
        repo = match.group("repo")
        results.append(GithubUrl(full_url=full_url, org_user=org_user, repo=repo))

    return results
