import json
import os
from typing import Optional, Dict

from config.paths import CUSTOM_SECTOR_PATH

FILE_PATH = os.path.join(os.path.dirname(__file__), CUSTOM_SECTOR_PATH)


def load_custom_sectors() -> Dict[str, str]:
    """Load user defined sector mappings from JSON file.

    Returns an empty dict if the file does not exist, is invalid or any
    error occurs. Creates the file if it's missing.
    """
    if os.path.exists(FILE_PATH):
        try:
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            return {}
        return {}
    else:
        try:
            with open(FILE_PATH, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        return {}


def save_custom_sectors(data: Dict[str, str]) -> None:
    """Persist the given sector mappings dictionary to disk."""
    try:
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def get_sector_from_cache(symbol: str) -> Optional[str]:
    """Return cached sector for the provided symbol if available."""
    data = load_custom_sectors()
    return data.get(symbol)


def add_sector(symbol: str, sector: str) -> None:
    """Add or update a symbol-to-sector mapping and persist it."""
    data = load_custom_sectors()
    if data.get(symbol) != sector:
        data[symbol] = sector
        save_custom_sectors(data)
