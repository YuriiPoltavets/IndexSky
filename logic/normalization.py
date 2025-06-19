import datetime
import math
from typing import Any, Dict, Optional

from .rating import calculate_skyindex_score
from config.normalization import SCALE_1D, SCALE_3D, SCALE_7D


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


def _tanh_percent(value: Any, scale: float) -> Optional[float]:
    """Return tanh-normalized percentage value.

    ``value`` may contain a string with a trailing ``%``. The numeric
    component is divided by 100 and then by ``scale`` before applying
    ``math.tanh``. The result is clamped to [-1, 1].
    """
    val = _parse_float(value)
    if val is None:
        return None
    try:
        normalized = math.tanh((val / 100.0) / scale)
    except Exception:
        return None
    return round(_clamp(normalized), 4)


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

    sector = _get_value(row, 'sector', 'Sector')
    if isinstance(sector, str):
        sector = sector.strip()
    if not sector:
        # Sector is required for normalization
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
                zacks_norm = round(_clamp((3 - z_int) / 2), 4)
        except ValueError:
            pass

    # --- PE Ratio ---
    pe_raw = _get_value(row, 'pe_ratio', 'PE Ratio')
    pe_norm: Optional[float] = None
    pe_val = _parse_float(pe_raw)
    if pe_val is not None:
        # Values below 25 are considered good, above 50 very bad
        pe_norm = round(_clamp(1 - (pe_val / 25)), 4)

    # --- Percent-based metrics ---
    def percent_norm(key1: str, key2: str) -> Optional[float]:
        raw = _get_value(row, key1, key2)
        val = _parse_float(raw)
        if val is not None:
            return round(_clamp(val / 100), 4)
        return None

    sector_growth_1d_norm = _tanh_percent(
        _get_value(row, 'sector_growth_1d'), SCALE_1D
    )
    sector_growth_3d_norm = _tanh_percent(
        _get_value(row, 'sector_growth_3d'), SCALE_3D
    )
    sector_growth_7d_norm = _tanh_percent(
        _get_value(row, 'sector_growth_7d'), SCALE_7D
    )

    eps_growth_norm = percent_norm('eps_growth', 'EPS Growth')
    revenue_growth_norm = percent_norm('revenue_growth', 'Revenue Growth')
    volume_change_norm = percent_norm('volume_change', 'Volume Change')

    metrics = {
        'zacks_rank_norm': zacks_norm,
        'pe_ratio_norm': pe_norm,
        'sector_growth_1d_norm': sector_growth_1d_norm,
        'sector_growth_3d_norm': sector_growth_3d_norm,
        'sector_growth_7d_norm': sector_growth_7d_norm,
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
        'is_etf': None,
    }
