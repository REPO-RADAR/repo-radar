import os
import warnings

# Matches GitHub repo URLs (https or SSH) and captures:
#   - org/user as 'org_user'
#   - repository name as 'repo'
GITHUB_URL_REGEX = (
    r"(?:https?:\/\/|git@)?(?:www\.)?github\.com[\/:]"
    r"(?P<org_user>[\w_-]+)\/"
    r"(?P<repo>[\w-]+)"
    r"(?:\.git)?"
    r"(?:\/[^\s]*)?"
)

# URLs for github API
GITHUB_API_URL = "https://api.github.com"
GITHUB_API_USER_ENDPOINT = "https://api.github.com/user" # User Endpoint

# Set GitHub token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    warnings.warn("GITHUB_TOKEN environment variable is not set. GitHub API tests may fail.", UserWarning)
    
# Auth headers. GitHub access token must be appended to end of it to make HTTP requests.
GITHUB_AUTH_HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "https://github.com/REPO-RADAR/repo-radar",
}

# GitHub pagination settings
GITHUB_DEFAULT_PAGE = 1;
GITHUB_MAX_PAGINATED = 100;