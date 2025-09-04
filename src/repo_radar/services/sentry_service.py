from __future__ import annotations
from datetime import datetime
from typing import List, Tuple
from repo_radar.api import sentry_api

def _to_num(v) -> float:
    """Best-effort to coerce Sentry y-values to a float."""
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except Exception:
            return 0.0
    if isinstance(v, dict):
        # common keys Sentry uses
        for k in ("count", "value", "sum", "avg", "p50", "p95", "p99"):
            if k in v:
                return _to_num(v[k])
        # fallback: any first numeric-looking value
        for k, val in v.items():
            num = _to_num(val)
            if num != 0.0:
                return num
        return 0.0
    if isinstance(v, list):
        if not v:
            return 0.0
        # some responses are like [{"count": N}] or [N]
        # choose the first meaningful numeric
        for item in v:
            num = _to_num(item)
            if num != 0.0:
                return num
        # if all zero/none, return zero
        return 0.0
    return 0.0

def _parse_events_stats(resp) -> List[Tuple[datetime, float]]:
    """
    Normalize Sentry events-stats responses to [(datetime, float), ...]
    Handles shapes like:
      {"data": [[ts, 12], [ts, {"count":12}], [ts, [{"count":12}]], ...]}
      or {"data": {"seriesName": "...", "data": [[ts, 12], ...]}}
    """
    data = resp.get("data", [])
    # Some variants: data is dict with key "data"
    if isinstance(data, dict) and "data" in data:
        data = data["data"]

    out: List[Tuple[datetime, float]] = []
    for point in data:
        if not isinstance(point, (list, tuple)) or len(point) < 2:
            continue
        ts, val = point[0], point[1]
        try:
            # Sentry timestamps are ms since epoch
            dt = datetime.fromtimestamp(ts / 1000)
        except Exception:
            # If ts is already a datetime or seconds, try best effort
            try:
                dt = datetime.fromtimestamp(float(ts))
            except Exception:
                continue
        y = _to_num(val)
        out.append((dt, y))
    return out

def unresolved_issue_count_30d() -> int:
    issues, _ = sentry_api.list_issues_30d()
    return len(issues)

def top_error_titles(limit=5):
    issues, _ = sentry_api.list_issues_30d()
    pairs = []
    for i in issues:
        title = i.get("title", "")
        count = _to_num(i.get("count"))
        pairs.append((title, int(count)))
    pairs.sort(key=lambda x: x[1], reverse=True)
    return pairs[:limit]

def error_timeseries_30d():
    data = sentry_api.timeseries_events_30d(
        field="count()",
        query="event.type:error",
    )
    return _parse_events_stats(data)

def latency_p50_timeseries_30d():
    # requires performance (transaction) events in your Sentry project
    data = sentry_api.timeseries_events_30d(
        field="p50(transaction.duration)",
        query="event.type:transaction",
    )
    return _parse_events_stats(data)
