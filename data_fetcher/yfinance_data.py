import yfinance as yf

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


def get_sector_yf(symbol: str):
    """Return the normalized sector for the given stock symbol via yfinance.

    If the sector cannot be determined or does not match one of the
    predefined values, ``None`` is returned so the user can select it
    manually.
    """
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


def fetch_yfinance_metrics(symbol: str):
    """Return a dictionary of basic growth metrics via yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
    except Exception:
        return None

    def pct(val):
        try:
            return f"{float(val) * 100:.2f}%"
        except Exception:
            return None

    eps_growth = pct(info.get("earningsQuarterlyGrowth"))
    revenue_growth = pct(info.get("revenueGrowth") or info.get("revenueQuarterlyGrowth"))
    pe_ratio = info.get("trailingPE")

    volume = info.get("volume")
    avg_volume = info.get("averageVolume")
    volume_change = None
    if volume and avg_volume:
        try:
            volume_change = f"{((volume - avg_volume) / avg_volume) * 100:.2f}%"
        except Exception:
            volume_change = None

    return {
        "eps_growth": eps_growth,
        "revenue_growth": revenue_growth,
        "pe_ratio": pe_ratio,
        "volume_change": volume_change,
    }
