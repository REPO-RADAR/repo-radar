import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parent / "src"))

from dotenv import load_dotenv
load_dotenv()  # reads .env at repo root

from repo_radar.llm.provider import summarize_state

def build_metrics_text() -> str:
    # replace these placeholders with your real numbers when your GitHub collector is ready
    return "\n".join([
        "Window: last 30 days",
        "Repos: org/app1, org/app2",
        "Issues opened: 42",
        "Issues closed: 35",
        "Backlog Δ: +7",
        "High CVEs: 0",
        "Error rate: (Sentry TBD)",
    ])

def main():
    metrics_text = build_metrics_text()
    summary = summarize_state(metrics_text)
    print("\n=== Metrics ===\n" + metrics_text)
    print("\n=== LLM Summary ===\n" + summary)

if __name__ == "__main__":
    main()
