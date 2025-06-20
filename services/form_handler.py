from datetime import datetime
from flask import Request

from sector_manager import get_sector_from_cache, add_sector
from sector_growth_cache import (
    load_sector_growth,
    get_sector_growth,
    get_sector_growth_data,
)
from config.constants import HEADERS
from logic.normalization import normalize_row
from logic.save_handler import save_row
from .fetch_service import parse_data
from .metrics_cache import metrics_cache

# Prefetch sector growth metrics on startup
sector_growth_loaded = load_sector_growth()


def field_name(key: str) -> str:
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

            if action == "data_search" and symbol:
                sector = rows[i].get("Sector", "") or get_sector_from_cache(symbol) or ""

                # Основний парсинг з кешуванням
                parsed = parse_data(symbol, sector)
                for key, value in parsed.items():
                    if key == "Sector" and rows[i].get("Sector"):
                        continue
                    rows[i][key] = value

                # Assign row_class based on parse result
                if not parsed or parsed.get("Zacks") in (None, "", "N/A"):
                    rows[i]["row_class"] = "row-error"
                else:
                    rows[i]["row_class"] = "row-ok"

                # Якщо є сектор — додаємо Sector Growth
                sector = rows[i].get("Sector") or sector
                if sector:
                    rows[i]["Sector Growth"] = get_sector_growth(sector)

                rows[i]["Дата"] = datetime.today().strftime("%Y-%m-%d")

            elif action == "calculate":
                sector = rows[i].get("Sector", "").strip()
                if not symbol or not sector:
                    rows[i]["row_class"] = "row-error"
                    continue

                metrics = metrics_cache.get(symbol)
                if not metrics:
                    rows[i]["row_class"] = "row-error"
                    continue

                add_sector(symbol, sector)

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
                    "Zacks": metrics.get("zacks"),
                    "TipRanks": metrics.get("tipranks"),
                    "Sector Growth 1d": sg1,
                    "Sector Growth 3d": sg3,
                    "Sector Growth 7d": sg7,
                    "sector_growth_1d": sg1,
                    "sector_growth_3d": sg3,
                    "sector_growth_7d": sg7,
                    "Дата": datetime.today().strftime("%Y-%m-%d"),
                }

                normalized = normalize_row(row_data)
                if normalized is None:
                    rows[i]["row_class"] = "row-error"
                    continue

                save_res = save_row(normalized)
                rows[i]["skyindex_score"] = normalized.get("skyindex_score")
                rows[i]["Дата"] = normalized.get("date")

                rows[i]["row_class"] = (
                    "row-ok" if save_res.get("status") == "ok" else "row-error"
                )

    return rows
