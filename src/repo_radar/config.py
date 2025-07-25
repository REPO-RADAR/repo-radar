# Matches GitHub repo URLs (https or SSH) and captures:
#   - org/user as 'org_user'
#   - repository name as 'repo'
GITHUB_URL_REGEX = r"(?:https?:\/\/|git@)?(?:www\.)?github\.com[\/:](?P<org_user>[\w_-]+)\/(?P<repo>[\w-]+?)(?:\.git)?(?:\/.*)?$"
