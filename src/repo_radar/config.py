# Matches GitHub repo URLs (https or SSH) and captures:
#   - org/user as 'org_user'
#   - repository name as 'repo'

from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

GITHUB_URL_REGEX = (
    r"(?:https?:\/\/|git@)?(?:www\.)?github\.com[\/:]"
    r"(?P<org_user>[\w_-]+)\/"
    r"(?P<repo>[\w-]+)"
    r"(?:\.git)?"
    r"(?:\/[^\s]*)?"
)

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