import re
from typing import List
from .github_url import GithubUrl


# Should move this to a config file
GITHUB_URL_REGEX = re.compile(
    r"(?:https?:\/\/|git@)?(?:www\.)?github\.com[\/:](?P<org_user>[\w_-]+)\/(?P<repo>[\w-]+?)(?:\.git)?(?:\/.*)?$"
)


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
    matches = GITHUB_URL_REGEX.finditer(text)
    results = []

    for match in matches:
        full_url = match.group()
        org_user = match.group("org_user")
        repo = match.group("repo")
        results.append(GithubUrl(full_url=full_url, org_user=org_user, repo=repo))

    return results
