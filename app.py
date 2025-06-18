from flask import Flask, render_template, request, jsonify
from datetime import datetime
from data_fetcher import get_zacks_rank, fetch_tipranks_data
from sector_manager import get_sector_from_cache, add_sector
from data_fetcher.yfinance_data import get_sector_yf
from logic.normalization import normalize_row
from logic.save_handler import save_row
from sector_growth_cache import (
    load_sector_growth,
    get_sector_growth,
    get_sector_growth_data,
)

# Prefetch sector growth metrics on startup
sector_growth_loaded = load_sector_growth()

app = Flask(__name__)

# Заголовки метрик у таблиці
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

# Варіанти секторів для випадаючого списку
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
    """Перетворює назву стовпця на ім'я поля форми"""
    return key.lower().replace(' ', '_')

def empty_row():
    return {
        "Symbol": "",
        **{key: "" for key in HEADERS},
        "skyindex_score": None,
        "Дата": "",
        "row_class": ""
    }

def parse_data(symbol):
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
        "Volume Change": ""
    }


@app.route("/fetch-data", methods=["POST"])
def fetch_data():
    """Return parsed data for a single stock symbol."""
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    symbol = payload.get("symbol") if isinstance(payload, dict) else None
    row_index = payload.get("rowIndex") if isinstance(payload, dict) else None
    if not symbol or not str(symbol).strip():
        return jsonify({"error": "Symbol is required"}), 400

    symbol = str(symbol).strip().upper()
    sector = ""
    if isinstance(payload.get("sector"), str):
        sector = payload["sector"].strip()

    try:
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
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    default_count = 5
    rows_count = default_count
    if request.method == 'POST' and request.form.get('rows_count'):
        try:
            rows_count = max(1, min(50, int(request.form.get('rows_count'))))
        except:
            rows_count = default_count

    rows = [empty_row() for _ in range(rows_count)]

    if request.method == 'POST':
        action = request.form.get('action')

        for i in range(rows_count):
            symbol = request.form.get(f'symbol_{i}', '').upper()
            rows[i]['Symbol'] = symbol

            # Завантажити поточні значення з форми
            for key in HEADERS:
                form_key = f"{field_name(key)}_{i}"
                rows[i][key] = request.form.get(form_key, '')

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

                rows[i]["Дата"] = datetime.today().strftime('%Y-%m-%d')

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
                    "Дата": datetime.today().strftime('%Y-%m-%d'),
                }

                normalized = normalize_row(row_data)
                if normalized is None:
                    rows[i]["row_class"] = "row-error"
                    continue

                # Persist custom sector mapping after any edits
                if symbol and sector:
                    add_sector(symbol, sector)

                save_res = save_row(normalized)
                rows[i]["skyindex_score"] = normalized.get("skyindex_score")
                rows[i]["Дата"] = normalized.get("date")

                if save_res.get("status") == "ok":
                    rows[i]["row_class"] = "row-ok"
                else:
                    rows[i]["row_class"] = "row-error"

    return render_template('index.html', headers=HEADERS, rows=rows, sectors=SECTOR_OPTIONS,
                           sector_growth_loaded=sector_growth_loaded)

if __name__ == '__main__':
    app.run(debug=True)
