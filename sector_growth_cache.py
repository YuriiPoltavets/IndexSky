"""Cache and provide sector growth metrics based on ETF performance."""

from __future__ import annotations

import datetime

import yfinance as yf

from sector_etf_map import SECTOR_TO_ETF

# In-memory cache structure populated at application startup
SECTOR_GROWTH_CACHE: dict[str, dict[str, str]] = {}


def load_sector_growth() -> bool:
    """Fetch and cache recent growth metrics for all sectors.

    Returns ``True`` if data for every sector could be fetched, otherwise
    ``False``.
    """
    global SECTOR_GROWTH_CACHE
    SECTOR_GROWTH_CACHE = {}
    all_ok = True
    today = datetime.date.today().strftime("%Y-%m-%d")

    for sector, etf in SECTOR_TO_ETF.items():
        try:
            ticker = yf.Ticker(etf)
            hist = ticker.history(period="8d")
            closes = hist["Close"].dropna().tolist()
            if len(closes) < 7:
                all_ok = False
                continue

            g1 = (closes[-1] - closes[-2]) / closes[-2]
            g3 = (closes[-1] - closes[-4]) / closes[-4]
            g7 = (closes[-1] - closes[0]) / closes[0]

            SECTOR_GROWTH_CACHE[sector] = {
                "1d": f"{g1 * 100:.2f}%",
                "3d": f"{g3 * 100:.2f}%",
                "7d": f"{g7 * 100:.2f}%",
                "updated": today,
            }
        except Exception:
            all_ok = False

    return all_ok


def get_sector_growth(sector: str) -> str:
    """Return the 1-day growth percentage for the given sector."""
    return SECTOR_GROWTH_CACHE.get(sector, {}).get("1d", "")


def get_sector_growth_data(sector: str) -> dict[str, str]:
    """Return cached growth metrics dictionary for the given sector."""
    return SECTOR_GROWTH_CACHE.get(sector, {})
