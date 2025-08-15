from __future__ import annotations
from typing import List, Tuple
from pathlib import Path
import matplotlib.pyplot as plt

def save_language_bar_chart(pairs: List[Tuple[str, float]], out_path: str | Path) -> Path:
    """
    pairs: [("Python", 55.2), ("TypeScript", 21.0), ...]
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    labels = [p[0] for p in pairs]
    values = [p[1] for p in pairs]

    plt.figure(figsize=(8, 4.5))
    plt.bar(labels, values)            # default colors are fine
    plt.xticks(rotation=30, ha="right")
    plt.ylabel("Language usage (%)")
    plt.title("Language composition across selected repos")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path