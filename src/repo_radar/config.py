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

# URL for github API
GITHUB_API_URL = "https://api.github.com"