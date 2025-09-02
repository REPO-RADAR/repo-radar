import sys, pathlib, os
sys.path.append(str(pathlib.Path(__file__).resolve().parent / "src"))

from dotenv import load_dotenv
load_dotenv()  # reads .env at repo root

from repo_radar.services.sentry_service import (
    unresolved_issue_count_30d, top_error_titles, error_timeseries_30d, latency_p50_timeseries_30d
)
from repo_radar.reports.charts import save_language_bar_chart

from typing import List
from repo_radar.models.github_url import GitHubUrl
from repo_radar.services.github_service import GitHubService
from repo_radar.services.lang_analytics import merge_language_maps, to_percentages
from repo_radar.reports.charts import save_language_bar_chart
from repo_radar.llm.provider import summarize_state

# --- config via .env (recommended) ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
# Example repos (replace with your real ones)
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

def metrics_text_from_lang(repos: List[GitHubUrl], lang_pairs: list[tuple[str, float]]) -> str:
    top5 = lang_pairs[:5]
    lang_str = ", ".join(f"{k} {v:.1f}%" for k, v in top5) if top5 else "n/a"
    return "\n".join([
        "Window: last 30 days",
        f"Repos: {', '.join([r.repo_path() for r in repos])}",
        f"Top languages: {lang_str}",
        "Issues opened: TBD",
        "Issues closed: TBD",
        "Backlog Δ: TBD",
        "High CVEs: TBD",
        "Error rate: (Sentry TBD)",
    ])

def write_simple_html(summary: str, chart_path: str, out_file="reports/report.html"):
    p = pathlib.Path(out_file)
    p.parent.mkdir(parents=True, exist_ok=True)

    summary_html = summary.replace("\n", "<br>")  # <-- do it here

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Repo Radar Report</title>
<style>body{{font-family:system-ui;margin:24px}} img{{max-width:700px}}</style>
</head><body>
<h1>Repo Radar — MVP Report</h1>
<h2>LLM overview</h2>
<p>{summary_html}</p>
<h2>Languages (%)</h2>
<img src="languages.png" alt="Languages bar chart">
</body></html>"""
    p.write_text(html, encoding="utf-8")
    print(f"✓ HTML report: {p.resolve()}")

def main():
    if not GITHUB_TOKEN:
        print("⚠ GITHUB_TOKEN not set. Put it in .env or env and re-run.")
        return

    # 1) GitHub → languages → %
    svc = GitHubService(GITHUB_TOKEN)
    lang_pairs = collect_language_percentages(svc, REPOS)

    # 2) Save chart
    chart_path = save_language_bar_chart(lang_pairs, "reports/languages.png")
    print(f"✓ Saved chart: {chart_path}")

    # 3) Build metrics + LLM summary
    metrics_text = metrics_text_from_lang(REPOS, lang_pairs)
    summary = summarize_state(metrics_text)

    # 4) CLI output + simple HTML
    print("\n=== Metrics ===")
    print(metrics_text)
    print("\n=== LLM Summary ===")
    print(summary)
    write_simple_html(summary, str(chart_path))

if __name__ == "__main__":
    main()
