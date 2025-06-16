import datetime
from typing import Any, Dict, Optional

from .rating import calculate_skyindex_score


def _get_value(data: Dict[str, Any], *keys: str) -> Optional[str]:
    """Return first matching key from data in case-insensitive manner."""
    lower = {k.lower(): v for k, v in data.items()}
    for key in keys:
        if key.lower() in lower:
            return lower[key.lower()]
    return None


def _parse_float(value: Any) -> Optional[float]:
    try:
        if isinstance(value, str):
            value = value.replace('%', '').strip()
        return float(value)
    except (TypeError, ValueError):
        return None


def _clamp(value: float, min_val: float = -1.0, max_val: float = 1.0) -> float:
    return max(min_val, min(max_val, value))


def normalize_row(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Normalize a raw stock row into the format stored in the database.

    If ``symbol`` or ``date`` cannot be parsed, ``None`` is returned to
    signal that this row should be skipped.
    """
    symbol = _get_value(row, 'symbol', 'Symbol')
    if isinstance(symbol, str):
        symbol = symbol.strip().upper() or None
    if not symbol:
        return None

    date_str = _get_value(row, 'date', 'Дата')
    if isinstance(date_str, str):
        date_str = date_str.strip()
        try:
            # validate format if possible
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            date_str = None
    else:
        date_str = None
    if not date_str:
        return None

    # --- Zacks Rank ---
    zacks_raw = _get_value(row, 'zacks', 'Zacks')
    zacks_norm: Optional[float] = None
    if zacks_raw is not None:
        try:
            z_int = int(str(zacks_raw).strip())
            if 1 <= z_int <= 5:
                zacks_norm = _clamp((3 - z_int) / 2)
        except ValueError:
            pass

    # --- PE Ratio ---
    pe_raw = _get_value(row, 'pe_ratio', 'PE Ratio')
    pe_norm: Optional[float] = None
    pe_val = _parse_float(pe_raw)
    if pe_val is not None:
        # Values below 25 are considered good, above 50 very bad
        pe_norm = _clamp(1 - (pe_val / 25))

    # --- Percent-based metrics ---
    def percent_norm(key1: str, key2: str) -> Optional[float]:
        raw = _get_value(row, key1, key2)
        val = _parse_float(raw)
        if val is not None:
            return _clamp(val / 100)
        return None

    sector_growth_norm = percent_norm('sector_growth', 'Sector Growth')
    eps_growth_norm = percent_norm('eps_growth', 'EPS Growth')
    revenue_growth_norm = percent_norm('revenue_growth', 'Revenue Growth')
    volume_change_norm = percent_norm('volume_change', 'Volume Change')

    metrics = {
        'zacks_rank_norm': zacks_norm,
        'pe_ratio_norm': pe_norm,
        'sector_growth_norm': sector_growth_norm,
        'eps_growth_norm': eps_growth_norm,
        'revenue_growth_norm': revenue_growth_norm,
        'volume_change_norm': volume_change_norm,
    }

    # If all normalized values are None → treat row as invalid
    if all(v is None for v in metrics.values()):
        return None

    skyindex_score = calculate_skyindex_score(metrics)

    return {
        'symbol': symbol,
        'date': date_str,
        'metrics': metrics,
        'open_price': None,
        'close_price': None,
        'price_change_today': None,
        'price_at_parse': None,
        'skyindex_score': skyindex_score,
    }
