"""Utility to run multiple fetchers."""

from typing import List, Dict

from .zacks import ZacksFetcher
from .tipranks import TipranksFetcher
from .yfinance_data import YFinanceFetcher


class FetcherManager:
    """Manage and execute a collection of data fetchers."""

    def __init__(self) -> None:
        self.fetchers: List = [
            ZacksFetcher(),
            TipranksFetcher(),
            YFinanceFetcher(),
        ]

    def fetch_all(self, symbol: str) -> Dict:
        """Fetch data from all providers and merge the results."""
        result: Dict = {}
        for fetcher in self.fetchers:
            try:
                data = fetcher.fetch(symbol)
                if isinstance(data, dict):
                    result.update(data)
            except Exception as exc:
                print(f"Error in {fetcher.__class__.__name__}: {exc}")
        return result
