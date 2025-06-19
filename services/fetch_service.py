from datetime import datetime
from typing import Optional, Dict

from fetchers.manager import FetcherManager
from fetchers.zacks import ZacksFetcher
from fetchers.tipranks import TipranksFetcher
from fetchers.yfinance_data import get_sector_yf
from sector_manager import get_sector_from_cache
from sector_growth_cache import get_sector_growth

fetcher_manager = FetcherManager()
zacks_fetcher = ZacksFetcher()
tipranks_fetcher = TipranksFetcher()


def build_stock_response(symbol: str, sector: str = "", row_index: Optional[int] = None) -> Dict:
    """Fetch metrics for a single stock symbol and assemble JSON response."""
    if not symbol or not str(symbol).strip():
        raise ValueError("Symbol is required")

    symbol = str(symbol).strip().upper()
    if not sector:
        sector = get_sector_from_cache(symbol) or get_sector_yf(symbol) or ""

    fetched = fetcher_manager.fetch_all(symbol)

    zacks_raw = fetched.get("zacks")
    zacks = int(zacks_raw) if str(zacks_raw).isdigit() else None

    tip_val = fetched.get("tipranks")
    tipranks = int(tip_val) if isinstance(tip_val, (int, float)) else None
    if tipranks is not None:
        print(f"🎯 TipRanks score parsed: {tipranks}")

    sector_growth = ""
    if sector:
        try:
            sector_growth = get_sector_growth(sector)
        except Exception:
            sector_growth = ""

    result = {
        "symbol": symbol,
        "zacks": zacks,
        "tipranks": tipranks,
        "sector": sector,
        "sector_growth": sector_growth,
        "date": datetime.today().strftime("%Y-%m-%d"),
    }

    if row_index is not None:
        result["rowIndex"] = row_index

    return result


def parse_data(symbol: str) -> Dict:
    """Return basic info about the given symbol for form prefilling."""
    if not symbol:
        return {}

    zacks_data = zacks_fetcher.fetch(symbol)
    tipranks_data = tipranks_fetcher.fetch(symbol)

    rank = zacks_data.get("zacks") if zacks_data else ""
    tip_val = tipranks_data.get("tipranks") if tipranks_data else ""
    if isinstance(tip_val, (int, float)):
        print(f"🎯 TipRanks score parsed: {tip_val}")

    sector = get_sector_from_cache(symbol)
    if sector is None:
        try:
            sector = get_sector_yf(symbol)
        except Exception:
            sector = ""

    if not isinstance(sector, str):
        sector = ""

    return {
        "Sector": sector or "",
        "Zacks": rank,
        "TipRanks": tip_val,
        "Sector Growth": "",
    }
