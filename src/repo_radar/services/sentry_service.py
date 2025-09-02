from __future__ import annotations
from datetime import datetime
from typing import Any, List, Tuple, Dict
from repo_radar.api import sentry_api

def unresolved_issue_count_30d() -> int:
    issues, _ = sentry_api.list_issues_30d()
    return len(issues)

def top_error_titles(limit=5) -> List[Tuple[str,int]]:
    issues, _ = sentry_api.list_issues_30d()
    # Each issue has 'title' and 'count' fields
    pairs = sorted([(i.get("title",""), int(i.get("count",0))) for i in issues],
                   key=lambda x: x[1], reverse=True)
    return pairs[:limit]

def error_timeseries_30d() -> List[Tuple[datetime,int]]:
    data = sentry_api.timeseries_events_30d(field="count()", query="event.type:error")
    pts = data.get("data", [])
    return [(datetime.fromtimestamp(p[0]/1000), int(p[1])) for p in pts]

def latency_p50_timeseries_30d() -> List[Tuple[datetime,float]]:
    data = sentry_api.timeseries_events_30d(field="p50(transaction.duration)", query="event.type:transaction")
    pts = data.get("data", [])
    # Sentry returns duration in milliseconds; keep as float ms
    return [(datetime.fromtimestamp(p[0]/1000), float(p[1])) for p in pts]
