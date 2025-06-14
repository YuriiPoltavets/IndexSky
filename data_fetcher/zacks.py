import requests
from bs4 import BeautifulSoup
import time
import random

def get_zacks_rank(symbol):
    time.sleep(random.uniform(1.0, 2.2))  # антиспам-затримка

    urls = [
        f"https://www.zacks.com/stock/quote/{symbol}?q={symbol}",
        f"https://www.zacks.com/funds/etf/{symbol}/profile?q={symbol}"
    ]

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
    }

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            # Крок 1: NA клас — повертаємо 0
            if soup.find("span", class_="rankrect_NA"):
                return "0"

            # Крок 2: Пошук валідного числа від 1 до 5
            for i in range(1, 6):
                span = soup.find("span", class_=f"rank_chip rankrect_{i}")
                if span and span.text.strip().isdigit():
                    return span.text.strip()

        except Exception as e:
            print(f"[!] Error parsing {symbol}: {e}")
            continue

    # Крок 3: нічого не знайдено
    return "error"
