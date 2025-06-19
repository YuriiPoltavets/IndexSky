from datetime import datetime
from typing import Dict

# Global in-memory cache for fetched metrics
metrics_cache: Dict[str, Dict] = {}


def reset_cache_if_stale() -> None:
    """Clear cache if the stored date is not today's date."""
    today = datetime.today().strftime("%Y-%m-%d")
    if any(entry.get("date") != today for entry in metrics_cache.values()):
        metrics_cache.clear()
