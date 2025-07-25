import re

GITHUB_URL_PATTERN = r"https?://(www\.)?github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+/?$"

def is_valid_github_repo_url(url: str) -> bool:
    return re.match(GITHUB_URL_PATTERN, url) is not None

def is_valid_github_username(username: str) -> bool:
    return re.match(r"^[a-zA-Z0-9-]{1,39}$", username) is not None
