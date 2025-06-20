# yfinance_data.py
"""YFinance based fetchers and utilities."""

from typing import Dict, Optional

import yfinance as yf

from .base_fetcher import BaseFetcher

# Mapping of raw yfinance sector names to the normalized sector values
# used in the dropdown UI.
SECTOR_MAP = {
    "Financial Services": "Financials",
    "Consumer Cyclical": "Consumer Discretionary",
    "Consumer Defensive": "Consumer Staples",
    "Basic Materials": "Materials",
    "Technology": "Technology",
    "Healthcare": "Healthcare",
    "Energy": "Energy",
    "Utilities": "Utilities",
    "Real Estate": "Real Estate",
    "Communication Services": "Communication Services",
    "Industrials": "Industrials",
}


class YFinanceFetcher(BaseFetcher):
    """Fetch basic financial metrics using yfinance."""

    def fetch(self, symbol: str) -> Dict[str, Optional[float]]:
        result: Dict[str, Optional[float]] = {
            "row_class": "row-ok",
            "eps": None,
            "revenue": None,
            "pe_ratio": None,
            "volume": None,
        }

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            eps = info.get("trailingEps") or info.get("epsTrailingEps") or info.get("epsTrailingTwelveMonths")
            revenue = info.get("totalRevenue")
            pe_ratio = info.get("trailingPE") or info.get("trailingPe")
            volume = info.get("volume")
            result.update({
                "eps": float(eps) if isinstance(eps, (int, float)) else None,
                "revenue": float(revenue) if isinstance(revenue, (int, float)) else None,
                "pe_ratio": float(pe_ratio) if isinstance(pe_ratio, (int, float)) else None,
                "volume": float(volume) if isinstance(volume, (int, float)) else None,
            })
        except Exception:
            result["row_class"] = "row-error"

        return result


def get_sector_yf(symbol: str) -> Optional[str]:
    """Return the normalized sector for the given stock symbol via yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        sector = info.get("sector")
        if isinstance(sector, str):
            normalized = SECTOR_MAP.get(sector)
            if normalized:
                return normalized
            return None
    except Exception:
        pass
    return None
