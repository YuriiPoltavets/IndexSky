"""Fetcher for TipRanks SmartScore data."""

import json
import random
import time
from typing import Dict, Optional

import requests

from config.delays import TIPRANKS_DELAY
from .base_fetcher import BaseFetcher

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


class TipranksFetcher(BaseFetcher):
    """Retrieve SmartScore from TipRanks."""

    def fetch(self, symbol: str) -> Dict[str, Optional[float]]:
        """Return the TipRanks score if available."""
        if not symbol:
            return {"tipranks": None}
        symbol = symbol.strip().lower()
        print(f"\n🔎 TipRanks for symbol: {symbol.upper()}")

        url = f"https://www.tipranks.com/stocks/{symbol}/stock-analysis/payload.json"
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Referer": f"https://www.tipranks.com/stocks/{symbol}/stock-analysis",
        }

        time.sleep(random.uniform(TIPRANKS_DELAY + 0.3, TIPRANKS_DELAY + 1.8))
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            print("✅ TipRanks response:", resp.status_code)
            if resp.status_code != 200 or not resp.text.strip():
                return {"tipranks": None}
            if "<html" in resp.text.lower():
                return {"tipranks": None}
            try:
                data = resp.json()
            except json.JSONDecodeError:
                return {"tipranks": None}
            stocks = data.get("models", {}).get("stocks", [])
            for i in reversed(range(len(stocks))):
                stock = stocks[i]
                smart = stock.get("smartScore")
                if isinstance(smart, dict) and "value" in smart:
                    score = smart["value"]
                    return {"tipranks": float(score)}
            return {"tipranks": None}
        except Exception as e:
            print(f"💥 Exception during TipRanks fetch: {e}")
            return {"tipranks": None}


# Backward compatible alias
fetch_tipranks_data = TipranksFetcher().fetch
