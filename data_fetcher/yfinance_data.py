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
