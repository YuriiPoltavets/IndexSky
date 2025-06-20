from datetime import datetime
from typing import Optional, Dict, List

from .metrics_cache import metrics_cache

from fetchers.manager import FetcherManager
from fetchers.yfinance_data import get_sector_yf
from sector_manager import get_sector_from_cache
from sector_growth_cache import get_sector_growth

fetcher_manager = FetcherManager()


def build_stock_response(
    symbol: str,
    sector: str = "",
    row_index: Optional[int] = None,
    log_messages: Optional[List[str]] = None,
) -> Dict:
    """Fetch metrics for a single stock symbol and assemble JSON response.

    Parsed metrics are stored in ``metrics_cache`` for later use by the
    ``calculate`` step.
    """
    if not symbol or not str(symbol).strip():
        raise ValueError("Symbol is required")

    symbol = str(symbol).strip().upper()
    if not sector:
        sector = get_sector_from_cache(symbol) or get_sector_yf(symbol) or ""

    if log_messages is None:
        fetched = fetcher_manager.fetch_all(symbol)
    else:
        fetched = fetcher_manager.fetch_all(symbol, log_messages)

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

    today = datetime.today().strftime("%Y-%m-%d")

    # Update global cache with all fetched metrics
    metrics_cache.pop(symbol, None)
    metrics_cache[symbol] = {
        "symbol": symbol,
        "zacks": zacks,
        "tipranks": tipranks,
        "sector": sector,
        "date": today,
        **{k: v for k, v in fetched.items() if k not in {"zacks", "tipranks"}},
    }

    valid = bool(sector and zacks is not None and tipranks is not None)

    result = {
        "symbol": symbol,
        "zacks": zacks,
        "tipranks": tipranks,
        "sector": sector,
        "sector_growth": sector_growth,
        "date": today,
        "row_class": "row-ok" if valid else "row-error",
    }

    if row_index is not None:
        result["rowIndex"] = row_index

    return result


def parse_data(symbol: str, sector: str = "") -> Dict:
    """Return basic info about the given symbol for form prefilling.

    This function reuses ``build_stock_response`` so that caching logic is
    consistent between the AJAX and fallback form workflows.
    """
    if not symbol:
        return {}

    result = build_stock_response(symbol, sector)

    return {
        "Sector": result.get("sector", ""),
        "Zacks": result.get("zacks"),
        "TipRanks": result.get("tipranks"),
        "Sector Growth": result.get("sector_growth", ""),
    }
