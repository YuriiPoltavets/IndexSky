from typing import Any, Dict, Optional


def calculate_skyindex_score(metrics: Dict[str, Any]) -> Optional[float]:
    """Returns the normalized Zacks Rank as the skyindex_score."""
    value = metrics.get("zacks_rank_norm")
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
