from flask import Flask, render_template, request, jsonify
from datetime import datetime
from data_fetcher.zacks import get_zacks_rank
from sector_manager import get_sector_from_cache, add_sector
from data_fetcher.yfinance_data import get_sector_yf
from logic.normalization import normalize_row
from logic.save_handler import save_row
from sector_growth_cache import load_sector_growth

# Prefetch sector growth metrics on startup
sector_growth_loaded = load_sector_growth()

app = Flask(__name__)

# Заголовки метрик у таблиці
HEADERS = [
    "Sector",
    "Zacks",
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
        "Дата": ""
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


@app.route("/save", methods=["POST"])
def save_data():
    """Normalize and save rows of stock data from JSON."""
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    if not isinstance(payload, list):
        return jsonify({"error": "Expected list of rows"}), 400

    results = []
    for row in payload:
        if not isinstance(row, dict):
            results.append({"symbol": None, "status": "error", "reason": "invalid row format"})
            continue

        symbol = row.get("symbol") or row.get("Symbol")
        if isinstance(symbol, str):
            symbol = symbol.strip().upper() or None

        # Skip completely blank rows (no symbol and no data)
        if not symbol and all(not str(row.get(key, '')).strip() for key in HEADERS):
            continue

        # Sector is required if symbol is provided
        sector = row.get("Sector") or row.get("sector")
        if isinstance(sector, str):
            sector = sector.strip()
        if symbol and not sector:
            results.append({"symbol": symbol, "status": "error", "reason": "Missing sector", "field": "Sector"})
            continue

        if symbol and sector:
            add_sector(symbol, sector)

        normalized = normalize_row(row)
        if normalized is None:
            results.append({"symbol": symbol, "status": "error", "reason": "invalid input"})
            continue

        results.append(save_row(normalized))

    return jsonify(results)


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

            if action == "parse" and symbol:
                parsed = parse_data(symbol)
                for key, value in parsed.items():
                    rows[i][key] = value
                rows[i]['Дата'] = datetime.today().strftime('%Y-%m-%d')
            elif action == "save":
                if symbol and rows[i].get('Sector'):
                    add_sector(symbol, rows[i]['Sector'])
                    rows[i]["Дата"] = datetime.today().strftime('%Y-%m-%d')

    return render_template('index.html', headers=HEADERS, rows=rows, sectors=SECTOR_OPTIONS,
                           sector_growth_loaded=sector_growth_loaded)

if __name__ == '__main__':
    app.run(debug=True)
