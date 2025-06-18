from datetime import datetime
from typing import Optional, Dict

from data_fetcher import get_zacks_rank, fetch_tipranks_data
from data_fetcher.yfinance_data import get_sector_yf
from sector_manager import get_sector_from_cache
from sector_growth_cache import get_sector_growth


def build_stock_response(symbol: str, sector: str = "", row_index: Optional[int] = None) -> Dict:
    """Fetch metrics for a single stock symbol and assemble JSON response."""
    if not symbol or not str(symbol).strip():
        raise ValueError("Symbol is required")

    symbol = str(symbol).strip().upper()
    if not sector:
        sector = get_sector_from_cache(symbol) or get_sector_yf(symbol) or ""
    try:
        zacks_raw = get_zacks_rank(symbol)
        zacks = int(zacks_raw) if str(zacks_raw).isdigit() else None
    except Exception:
        zacks = None

    try:
        tip = fetch_tipranks_data(symbol)
        tip_val = tip.get("tipranks_score") if tip else None
        tipranks = int(tip_val) if isinstance(tip_val, (int, float)) else None
    except Exception:
        tipranks = None

    sector_growth = ""
    if sector:
        try:
            sector_growth = get_sector_growth(sector)
        except Exception:
            sector_growth = ""

    result = {
        "zacks": zacks,
        "tipranks": tipranks,
        "sector": sector,
        "sector_growth": sector_growth,
        "eps": "",
        "revenue": "",
        "pe_ratio": "",
        "volume": "",
        "date": datetime.today().strftime("%Y-%m-%d"),
    }
    if row_index is not None:
        result["rowIndex"] = row_index
    return result


def parse_data(symbol: str) -> Dict:
    """Return basic info about the given symbol for form prefilling."""
    if not symbol:
        return {}
    rank = get_zacks_rank(symbol)
    sector = get_sector_from_cache(symbol)
    if sector is None:
        try:
            sector = get_sector_yf(symbol)
        except Exception:
            sector = ""
    if not isinstance(sector, str):
        sector = ""
    return {
        "Sector": sector if sector else "",
        "Zacks": rank,
        "Sector Growth": "",
        "EPS Growth": "",
        "Revenue Growth": "",
        "PE Ratio": "",
        "Volume Change": "",
    }
