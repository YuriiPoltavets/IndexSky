from flask import Flask, render_template_string, request
from datetime import datetime
from data_fetcher.zacks import get_zacks_rank
from logic.rating import evaluate_rating

app = Flask(__name__)

# HTML-шаблон
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Індекс Скай</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f0f2f5; padding: 40px; }
        input, button { padding: 6px; font-size: 14px; margin: 2px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 6px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
    </style>
</head>
<body>
    <h1>Індекс Скай — Масова Оцінка Акцій</h1>
    <form method="POST">
        <label>Кількість рядків: </label>
        <input type="number" name="rows_count" min="1" max="50" value="{{ rows|length }}">
        <button name="action" value="resize">Оновити</button>
        <br><br>
        <table>
            <tr>
                <th>Symbol</th>
                {% for header in headers %}
                    <th>{{ header }}</th>
                {% endfor %}
                <th>Оцінка</th>
                <th>Дата</th>
            </tr>
            {% for i in range(rows|length) %}
            <tr>
                <td><input type="text" name="symbol_{{ i }}" value="{{ rows[i]['Symbol'] }}"></td>
                {% for header in headers %}
                    <td><input type="text" name="{{ header }}_{{ i }}" value="{{ rows[i][header] }}"></td>
                {% endfor %}
                <td>{{ rows[i]['Оцінка'] }}</td>
                <td>{{ rows[i]['Дата'] }}</td>
            </tr>
            {% endfor %}
        </table>
        <br>
        <button name="action" value="parse">ПАРСІНГ</button>
        <button name="action" value="evaluate">ОЦІНКА</button>
    </form>
</body>
</html>
"""

# Заголовки метрик
HEADERS = [
    "Zacks Rank",
    "Sector Growth",
    "EPS Growth",
    "Revenue Growth",
    "PE Ratio",
    "Volume Change"
]

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
    return {
        "Zacks Rank": rank,
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

            if action == "parse" and symbol:
                parsed = parse_data(symbol)
                for key in HEADERS:
                    rows[i][key] = parsed.get(key, '')
                rows[i]['Дата'] = datetime.today().strftime('%Y-%m-%d')
            elif action == "evaluate":
                for key in HEADERS:
                    rows[i][key] = request.form.get(f'{key}_{i}', '')
                rows[i]['Оцінка'] = evaluate_rating(rows[i])
                rows[i]['Дата'] = datetime.today().strftime('%Y-%m-%d')

    return render_template_string(HTML_TEMPLATE, headers=HEADERS, rows=rows)

if __name__ == '__main__':
    app.run(debug=True)
