import random
import time
from typing import Dict, Optional

import requests


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"


def fetch_tipranks_data(symbol: str) -> Optional[Dict]:
    """Fetch TipRanks Smart Score for the given symbol.

    Returns a dictionary containing ``tipranks_score`` and ``is_etf`` or
    ``None`` if the request fails.
    """
    if not symbol:
        return None

    symbol = symbol.strip().lower()
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": "https://www.tipranks.com/",
    }

    # Determine if the symbol is an ETF
    is_etf = -1
    try:
        resp = requests.get(f"https://www.tipranks.com/etf/{symbol}", headers=headers, timeout=10)
        if resp.status_code == 200:
            is_etf = 1
    except Exception:
        pass

    kind = "etf" if is_etf == 1 else "stocks"
    time.sleep(random.uniform(0.5, 1.1))

    headers["Referer"] = f"https://www.tipranks.com/{kind}/{symbol}"
    url = f"https://www.tipranks.com/api/{kind}/{symbol}/forecast"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        score = data.get("analystConsensus", {}).get("score")
        if score is None:
            return None
        return {"tipranks_score": float(score), "is_etf": is_etf}
    except Exception:
        return None
