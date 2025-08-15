from __future__ import annotations
import hashlib, json, os, time
from pathlib import Path
from typing import Optional
from litellm import completion

# cache at project root so it persists across runs
CACHE_DIR = Path(__file__).resolve().parents[2] / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

API_BASE = "https://openrouter.ai/api/v1"
PRIMARY_MODEL = "openrouter/openai/gpt-5-mini"
DAILY_LIMIT = int(os.getenv("LLM_DAILY_LIMIT", "10"))
TIMEOUT = int(os.getenv("LLM_TIMEOUT", "20"))

def _cache_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

def _extra_headers() -> dict:
    h: dict = {}
    ref = os.getenv("OPENROUTER_HTTP_REFERER")
    ttl = os.getenv("OPENROUTER_APP_TITLE")
    if ref: h["HTTP-Referer"] = ref
    if ttl: h["X-Title"] = ttl
    return h

def summarize_state(metrics_text: str, *, model: Optional[str] = None) -> str:
    """
    Budget-safe summary:
    - Skips if no OPENROUTER_API_KEY
    - Caches by metrics_text (identical input → no re-call)
    - Enforces DAILY_LIMIT calls per day
    """
    if not os.getenv("OPENROUTER_API_KEY"):
        return "(LLM disabled: OPENROUTER_API_KEY not set)"

    # cache
    key = _cache_key(metrics_text)
    cache_file = CACHE_DIR / f"summary_{key}.txt"
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")

    # throttle
    stamp = time.strftime("%Y%m%d")
    counter_file = CACHE_DIR / f"daily_count_{stamp}.json"
    try:
        count = json.loads(counter_file.read_text()).get("count", 0)
    except Exception:
        count = 0
    if count >= DAILY_LIMIT:
        return "(LLM skipped: daily limit reached)"

    messages = [
        {"role": "system", "content": "You are a concise engineering manager."},
        {"role": "user", "content": f"""
Summarize this engineering status for leadership.

Data:
{metrics_text}

Return:
- 3 bullets: notable trends/risks
- 3 bullets: recommended actions
- <=150 words
"""},
    ]

    try:
        resp = completion(
            model=model or PRIMARY_MODEL,
            messages=messages,
            temperature=0.2,
            timeout=TIMEOUT,
            api_base=API_BASE,
            extra_headers=_extra_headers(),
        )
        text = resp["choices"][0]["message"]["content"]
        cache_file.write_text(text, encoding="utf-8")
        counter_file.write_text(json.dumps({"count": count + 1}))
        return text
    except Exception as e:
        return f"(LLM error via OpenRouter: {e})"
