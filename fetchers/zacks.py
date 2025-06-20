"""Fetcher for Zacks rank value."""

import random
import time
from typing import Dict

import requests
from bs4 import BeautifulSoup

from config.delays import ZACKS_DELAY
from .base_fetcher import BaseFetcher


class ZacksFetcher(BaseFetcher):
    """Fetch the Zacks rank for a stock symbol."""

    def fetch(self, symbol: str) -> Dict[str, str]:
        """Return the Zacks rank as a dictionary with status class."""
        time.sleep(random.uniform(ZACKS_DELAY - 0.9, ZACKS_DELAY))

        result: Dict[str, str] = {"row_class": "row-ok", "zacks": "error"}

        urls = [
            f"https://www.zacks.com/stock/quote/{symbol}?q={symbol}",
            f"https://www.zacks.com/funds/etf/{symbol}/profile?q={symbol}",
        ]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
        }

        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, "html.parser")

                if soup.find("span", class_="rankrect_NA"):
                    result["zacks"] = "0"
                    return result

                for i in range(1, 6):
                    span = soup.find("span", class_=f"rank_chip rankrect_{i}")
                    if span and span.text.strip().isdigit():
                        result["zacks"] = span.text.strip()
                        return result
            except Exception as e:
                print(f"[!] Error parsing {symbol}: {e}")
                result["row_class"] = "row-error"
                continue

        result["row_class"] = "row-error"
        return result


# Backward compatible function alias
fetch_zacks_rank = ZacksFetcher().fetch
