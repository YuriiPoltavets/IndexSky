from typing import Any, Dict, Optional


def calculate_skyindex_score(metrics: Dict[str, Any]) -> Optional[float]:
    """Calculate a weighted score based on available normalized metrics."""
    weights_sum = 0.0
    score = 0.0

    zacks_val = metrics.get("zacks_rank_norm")
    if isinstance(zacks_val, (int, float)):
        score += 0.5 * float(zacks_val)
        weights_sum += 0.5

    tip_val = metrics.get("tipranks_score_norm")
    if isinstance(tip_val, (int, float)):
        score += 0.5 * float(tip_val)
        weights_sum += 0.5

    if weights_sum == 0:
        return None

    return round(score / weights_sum, 4)
