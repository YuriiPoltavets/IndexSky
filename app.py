from flask import Flask, render_template, request
from datetime import datetime
from data_fetcher.zacks import get_zacks_rank
from logic.rating import evaluate_rating
from sector_manager import get_sector_from_cache, add_sector
from data_fetcher.yfinance_data import get_sector_yf

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
    "Financial Services",
    "Healthcare",
    "Communication Services",
    "Consumer Cyclical",
    "Consumer Defensive",
    "Industrials",
    "Basic Materials",
    "Utilities",
    "Real Estate",
    "Energy",
    "Broad Market",
    "Bonds",
    "Innovation",
]

def field_name(key: str) -> str:
    """Перетворює назву стовпця на ім'я поля форми"""
    return key.lower().replace(' ', '_')

def empty_row():
    return {
        "Symbol": "",
        **{key: "" for key in HEADERS},
        "Оцінка": "-",
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
            elif action == "evaluate":
                rows[i]['Оцінка'] = evaluate_rating(rows[i])
                rows[i]['Дата'] = datetime.today().strftime('%Y-%m-%d')
            elif action == "save":
                if symbol and rows[i].get('Sector'):
                    add_sector(symbol, rows[i]['Sector'])
                    rows[i]["Дата"] = datetime.today().strftime('%Y-%m-%d')

    return render_template('index.html', headers=HEADERS, rows=rows, sectors=SECTOR_OPTIONS)

if __name__ == '__main__':
    app.run(debug=True)
