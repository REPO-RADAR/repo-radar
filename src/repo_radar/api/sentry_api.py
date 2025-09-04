from __future__ import annotations
import os, requests, functools

BASE = (os.getenv("SENTRY_API_BASE") or "https://repo-radar.sentry.io") + "/api/0"

def _headers():
    token = os.getenv("SENTRY_AUTH_TOKEN")
    if not token:
        raise RuntimeError("SENTRY_AUTH_TOKEN missing")
    return {"Authorization": f"Bearer {token}"}

def _org():
    v = os.getenv("SENTRY_ORG_SLUG"); 
    if not v: raise RuntimeError("SENTRY_ORG_SLUG missing")
    return v

def _project_slug():
    v = os.getenv("SENTRY_PROJECT_SLUG"); 
    if not v: raise RuntimeError("SENTRY_PROJECT_SLUG missing")
    return v

@functools.lru_cache(maxsize=1)
def _project_id() -> str:
    env_id = os.getenv("SENTRY_PROJECT_ID")
    if env_id:
        return str(env_id)
    # slug -> id resolve
    url = f"{BASE}/projects/{_org()}/{_project_slug()}/"
    r = requests.get(url, headers=_headers(), timeout=20)
    r.raise_for_status()
    return str(r.json().get("id"))

def list_issues_30d(query="is:unresolved", limit=100):
    # use org issues + numeric project id for robustness
    url = f"{BASE}/organizations/{_org()}/issues/"
    params = {
        "project": _project_id(),        # numeric ID
        "statsPeriod": "30d",
        "query": query,
        "limit": limit
    }
    r = requests.get(url, headers=_headers(), params=params, timeout=20)
    r.raise_for_status()
    return r.json(), r.headers.get("Link")

def timeseries_events_30d(field="count()", interval="1d", query="event.type:error"):
    url = f"{BASE}/organizations/{_org()}/events-stats/"
    params = {
        "project": _project_id(),   # must be the numeric ID
        "statsPeriod": "30d",
        "interval": interval,
        "query": query,
        "yAxis": field,
    }
    r = requests.get(url, headers=_headers(), params=params, timeout=30)
    r.raise_for_status()
    return r.json()
