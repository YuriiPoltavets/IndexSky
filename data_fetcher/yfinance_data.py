import yfinance as yf


def get_sector_yf(symbol: str) -> str:
    """Return the sector for the given stock symbol using yfinance.

    If the sector cannot be determined or an error occurs, return
    an empty string.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        sector = info.get("sector")
        if isinstance(sector, str):
            return sector
    except Exception:
        pass
    return ""
