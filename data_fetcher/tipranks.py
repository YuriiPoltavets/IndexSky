import json
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
)


def _find_in_dict(obj, key):
    """Yield all values of ``key`` recursively found in ``obj``."""

    if isinstance(obj, dict):
        if key in obj:
            yield obj[key]
        for v in obj.values():
            yield from _find_in_dict(v, key)
    elif isinstance(obj, list):
        for item in obj:
            yield from _find_in_dict(item, key)


def fetch_tipranks_data(symbol: str) -> Optional[Dict]:
    """Return TipRanks Smart Score for ``symbol``.

    The function scrapes the TipRanks analysis page and extracts the JSON
    data embedded in a ``<script>`` tag. ``None`` is returned if the data
    cannot be retrieved or parsed.
    """

    if not symbol:
        return None

    symbol = symbol.strip().lower()
    url = f"https://www.tipranks.com/stocks/{symbol}/stock-analysis"
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": "https://www.tipranks.com/",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        script = None
        for tag in soup.find_all("script"):
            content = tag.string or tag.text
            if content and "\"_meta\"" in content and "\"stocks\"" in content:
                script = content
                break

        if not script:
            return None

        data = json.loads(script)

        smart_score = None
        for val in _find_in_dict(data, "smartScore"):
            try:
                smart_score = float(val)
                break
            except (TypeError, ValueError):
                continue

        if smart_score is None:
            return None

        return {"tipranks_score": smart_score, "raw_data": data}

    except Exception:
        return None
