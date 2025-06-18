from datetime import datetime
from flask import Request

from sector_manager import get_sector_from_cache, add_sector
from sector_growth_cache import (
    load_sector_growth,
    get_sector_growth,
    get_sector_growth_data,
)
from logic.normalization import normalize_row
from logic.save_handler import save_row
from data_fetcher import fetch_tipranks_data
from .fetch_service import parse_data

# Prefetch sector growth metrics on startup
sector_growth_loaded = load_sector_growth()

# Table headers shown in the UI
HEADERS = [
    "Sector",
    "Zacks",
    "TipRanks",
    "Sector Growth",
    "EPS Growth",
    "Revenue Growth",
    "PE Ratio",
    "Volume Change",
]

# Dropdown options for sectors
SECTOR_OPTIONS = [
    "Technology",
    "Financials",
    "Healthcare",
    "Communication Services",
    "Consumer Discretionary",
    "Consumer Staples",
    "Industrials",
    "Materials",
    "Energy",
    "Utilities",
    "Real Estate",
]


def field_name(key: str) -> str:
    """Convert a table header into a form field name."""
    return key.lower().replace(" ", "_")


def empty_row():
    return {
        "Symbol": "",
        **{key: "" for key in HEADERS},
        "skyindex_score": None,
        "Дата": "",
        "row_class": "",
    }


def process_index_form(req: Request, default_count: int = 5):
    """Handle index form submission and return a list of rows."""
    rows_count = default_count
    if req.method == "POST" and req.form.get("rows_count"):
        try:
            rows_count = max(1, min(50, int(req.form.get("rows_count"))))
        except Exception:
            rows_count = default_count

    rows = [empty_row() for _ in range(rows_count)]

    if req.method == "POST":
        action = req.form.get("action")
        for i in range(rows_count):
            symbol = req.form.get(f"symbol_{i}", "").upper()
            rows[i]["Symbol"] = symbol

            for key in HEADERS:
                form_key = f"{field_name(key)}_{i}"
                rows[i][key] = req.form.get(form_key, "")

            sector = rows[i].get("Sector", "").strip()

            if action in ("data_search", "calculate") and symbol and sector:
                add_sector(symbol, sector)

            if action == "data_search" and symbol:
                if not rows[i].get("Sector"):
                    cached_sector = get_sector_from_cache(symbol)
                    if cached_sector:
                        rows[i]["Sector"] = cached_sector

                parsed = parse_data(symbol)
                for key, value in parsed.items():
                    if key == "Sector" and rows[i].get("Sector"):
                        continue
                    rows[i][key] = value

                tip_data = fetch_tipranks_data(symbol)
                if tip_data and tip_data.get("tipranks_score") is not None:
                    rows[i]["TipRanks"] = tip_data["tipranks_score"]

                sector = rows[i].get("Sector")
                if sector:
                    rows[i]["Sector Growth"] = get_sector_growth(sector)

                rows[i]["Дата"] = datetime.today().strftime("%Y-%m-%d")

            elif action == "calculate":
                if not symbol:
                    continue

                sector = rows[i].get("Sector", "")
                sector_growth = rows[i].get("Sector Growth", "")

                if sector and not sector_growth:
                    rows[i]["Sector Growth"] = get_sector_growth(sector)
                sg_data = get_sector_growth_data(sector) if sector else {}
                sg1 = rows[i]["Sector Growth"]
                sg3 = sg_data.get("3d", "")
                sg7 = sg_data.get("7d", "")

                row_data = {
                    "Symbol": symbol,
                    "Sector": sector,
                    "Zacks": rows[i].get("Zacks"),
                    "Sector Growth 1d": sg1,
                    "Sector Growth 3d": sg3,
                    "Sector Growth 7d": sg7,
                    "sector_growth_1d": sg1,
                    "sector_growth_3d": sg3,
                    "sector_growth_7d": sg7,
                    "EPS Growth": rows[i].get("EPS Growth"),
                    "Revenue Growth": rows[i].get("Revenue Growth"),
                    "PE Ratio": rows[i].get("PE Ratio"),
                    "Volume Change": rows[i].get("Volume Change"),
                    "Дата": datetime.today().strftime("%Y-%m-%d"),
                }

                normalized = normalize_row(row_data)
                if normalized is None:
                    rows[i]["row_class"] = "row-error"
                    continue

                if symbol and sector:
                    add_sector(symbol, sector)

                save_res = save_row(normalized)
                rows[i]["skyindex_score"] = normalized.get("skyindex_score")
                rows[i]["Дата"] = normalized.get("date")

                if save_res.get("status") == "ok":
                    rows[i]["row_class"] = "row-ok"
                else:
                    rows[i]["row_class"] = "row-error"

    return rows
