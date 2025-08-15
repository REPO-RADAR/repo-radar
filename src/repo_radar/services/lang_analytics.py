from __future__ import annotations
from typing import Dict, List, Tuple
from collections import Counter

def merge_language_maps(lang_maps: List[Dict[str, int]]) -> Dict[str, int]:
    """
    Given a list.
    """
    total = Counter()
    for m in lang_maps:
        total.update(m or {})
    return dict(total)

def to_percentages(byte_map: Dict[str, int]) -> List[Tuple[str, float]]:
    """
    Convert to sorted desc.
    """
    total = sum(byte_map.values()) or 1
    pairs = [(k, (v / total) * 100.0) for k, v in byte_map.items()]
    return sorted(pairs, key=lambda x: x[1], reverse=True)
