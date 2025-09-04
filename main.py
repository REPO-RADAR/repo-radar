import sys, pathlib, os
sys.path.append(str(pathlib.Path(__file__).resolve().parent / "src"))

from dotenv import load_dotenv
load_dotenv()  # reads .env at repo root

# --- Sentry SDK (optional) ---
from repo_radar.monitoring import sentry_sdk_init
sentry_sdk_init.init()

# --- Sentry service (read API) ---
from repo_radar.services.sentry_service import (
    unresolved_issue_count_30d,
    top_error_titles,
    error_timeseries_30d,
    latency_p50_timeseries_30d,
)

from typing import List
from repo_radar.models.github_url import GitHubUrl
from repo_radar.services.github_service import GitHubService
from repo_radar.services.lang_analytics import merge_language_maps, to_percentages
from repo_radar.reports.charts import save_language_bar_chart, save_line_chart  # <-- add save_line_chart
from repo_radar.llm.provider import summarize_state

# --- config via .env (recommended) ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

def _repos_from_env() -> list[GitHubUrl]:
    raw = os.getenv("GITHUB_REPOS", "")
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    repos: list[GitHubUrl] = []
    for p in parts:
        if p.startswith("https://github.com/"):
            p = p.replace("https://github.com/", "")
        owner, name = p.split("/", 1)
        repos.append(GitHubUrl(full_url="", org_user=owner, repo=name))
    return repos

REPOS = _repos_from_env()

def collect_language_percentages(svc: GitHubService, repos: List[GitHubUrl]):
    lang_maps = []
    for r in repos:
        langs = svc.get_languages(r)  # {"Python": 12345, ...}
        lang_maps.append(langs)
    merged = merge_language_maps(lang_maps)
    return to_percentages(merged)     # [("Python", 55.2), ...]

def metrics_text_from_sources(repos, lang_pairs):
    top5 = lang_pairs[:5]
    lang_str = ", ".join(f"{k} {v:.1f}%" for k, v in top5) if top5 else "n/a"

    # Sentry metrics (best effort)
    err_line = "n/a"
    top_errs_str = "n/a"
    try:
        err_count = unresolved_issue_count_30d()
        err_line = f"{err_count} unresolved issues (30d)"
        tops = top_error_titles()
        if tops:
            top_errs_str = "; ".join(f"{t} ({c})" for t, c in tops)
        else:
            top_errs_str = "none"
    except Exception as e:
        print(f"⚠ Sentry issues fetch failed: {e}")

    return "\n".join([
        "Window: last 30 days",
        f"Repos: {', '.join([r.repo_path() for r in repos])}",
        f"Top languages: {lang_str}",
        "Issues opened: TBD",
        "Issues closed: TBD",
        "Backlog Δ: TBD",
        "High CVEs: TBD",
        f"Sentry unresolved: {err_line}",
        f"Top Sentry errors: {top_errs_str}",
        "Perf: see charts for errors/latency p50",
    ])


def write_simple_html(summary: str, charts: list[str], out_file="reports/report.html"):
    p = pathlib.Path(out_file)
    p.parent.mkdir(parents=True, exist_ok=True)

    summary_html = summary.replace("\n", "<br>")
    imgs_html = "\n".join(
        f'<h2>{pathlib.Path(c).stem}</h2><img src="{pathlib.Path(c).as_posix()}" alt="{pathlib.Path(c).name}">'
        for c in charts
    )

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Repo Radar Report</title>
<style>body{{font-family:system-ui;margin:24px}} img{{max-width:700px; display:block; margin:8px 0}}</style>
</head><body>
<h1>Repo Radar — MVP Report</h1>
<h2>LLM overview</h2>
<p>{summary_html}</p>
{imgs_html}
</body></html>"""
    p.write_text(html, encoding="utf-8")
    print(f"✓ HTML report: {p.resolve()}")

def main():
    if not GITHUB_TOKEN:
        print("⚠ GITHUB_TOKEN not set. Put it in .env or env and re-run.")
        return

    chart_paths: list[str] = []  # always initialize

    # 1) GitHub → languages → %
    svc = GitHubService(GITHUB_TOKEN)
    lang_pairs = collect_language_percentages(svc, REPOS)

    # 2) Save language chart
    lang_chart = save_language_bar_chart(lang_pairs, "reports/languages.png")
    chart_paths.append(str(lang_chart))
    print(f"✓ Saved chart: {lang_chart}")

    # 3) Sentry charts (best effort)
    try:
        errs_series = error_timeseries_30d()
        if errs_series:
            err_chart = save_line_chart(
                errs_series, "Errors (last 30 days)", "Count", "reports/sentry_errors.png"
            )
            chart_paths.append(str(err_chart))
            print(f"✓ Saved chart: {err_chart}")

        p50_series = latency_p50_timeseries_30d()
        if p50_series:
            lat_chart = save_line_chart(
                p50_series, "Latency p50 (ms, 30d)", "ms", "reports/sentry_latency.png"
            )
            chart_paths.append(str(lat_chart))
            print(f"✓ Saved chart: {lat_chart}")
    except Exception as e:
        print(f"⚠ Could not fetch Sentry data: {e}")

    # 4) Build metrics + LLM summary
    metrics_text = metrics_text_from_sources(REPOS, lang_pairs)
    summary = summarize_state(metrics_text)

    # 5) CLI output + simple HTML
    print("\n=== Metrics ===")
    print(metrics_text)
    print("\n=== LLM Summary ===")
    print(summary)

    write_simple_html(summary, chart_paths)

if __name__ == "__main__":
    main()
