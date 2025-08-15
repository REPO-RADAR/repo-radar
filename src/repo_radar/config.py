from __future__ import annotations
import os
import warnings
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

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

LINK_HEADER_NEXT_REGEX = r'<([^>]+)>;\s*rel="next"'

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
GITHUB_MAX_PAGINATED = 100;
MAX_RETRIES = 5

# GitHub API rate limits
GITHUB_DEFAULT_RATE = 5000

#GitHub default delta for branch comparison in days
GITUB_DEFAULT_DELTA = 30

# Load .env from project root (parent of src/)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

@dataclass(frozen=True)
class LLMConfig:
    api_base: str = "https://openrouter.ai/api/v1"
    primary_model: str = "openrouter/openai/gpt-5o-mini"
    daily_limit: int = int(os.getenv("LLM_DAILY_LIMIT", "5"))
    timeout: int = int(os.getenv("LLM_TIMEOUT", "20"))
    api_key: str | None = os.getenv("OPENROUTER_API_KEY")
    http_referer: str | None = os.getenv("OPENROUTER_HTTP_REFERER")
    app_title: str | None = os.getenv("OPENROUTER_APP_TITLE", "Repo Radar")

LLM = LLMConfig()
