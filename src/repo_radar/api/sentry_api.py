from __future__ import annotations
import os, requests

BASE = "https://sentry.io/api/0"

def _headers():
    token = os.getenv("SENTRY_AUTH_TOKEN")
    if not token:
        raise RuntimeError("SENTRY_AUTH_TOKEN missing")
    return {"Authorization": f"Bearer {token}"}

def _org(): 
    v = os.getenv("SENTRY_ORG_SLUG"); 
    if not v: raise RuntimeError("SENTRY_ORG_SLUG missing"); 
    return v

def _project(): 
    v = os.getenv("SENTRY_PROJECT_SLUG"); 
    if not v: raise RuntimeError("SENTRY_PROJECT_SLUG missing"); 
    return v

def list_issues_30d(query="is:unresolved", limit=100):
    """Unresolved issues for last 30 days (first page)."""
    url = f"{BASE}/projects/{_org()}/{_project()}/issues/"
    params = {"statsPeriod": "30d", "query": query, "limit": limit}
    r = requests.get(url, headers=_headers(), params=params, timeout=20)
    r.raise_for_status()
    return r.json(), r.headers.get("Link")

def timeseries_events_30d(field="count()", interval="1d", query="event.type:error"):
    """
    High-level timeseries via Discover (Events API).
    field can be count(), failure_count(), p50(transaction.duration), apdex(), etc.
    """
    url = f"{BASE}/organizations/{_org()}/events-stats/"
    params = {
        "project": _project(),
        "statsPeriod": "30d",
        "interval": interval,
        "query": query,
        "yAxis": field,
    }
    r = requests.get(url, headers=_headers(), params=params, timeout=30)
    r.raise_for_status()
    # returns {"data":[[ts, value], ...], ...}
    return r.json()
