import json
import time
import random
import requests
from typing import Optional, Dict  # ✅ ІМПОРТ ПЕРЕД функцією

from config.delays import TIPRANKS_DELAY

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

def fetch_tipranks_data(symbol: str) -> Optional[Dict]:
    """Fetch TipRanks SmartScore for a given stock symbol."""

    if not symbol:
        return None

    symbol = symbol.strip().lower()
    print(f"\n🔎 TipRanks for symbol: {symbol.upper()}")

    url = f"https://www.tipranks.com/stocks/{symbol}/stock-analysis/payload.json"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Referer": f"https://www.tipranks.com/stocks/{symbol}/stock-analysis",
    }

    time.sleep(random.uniform(TIPRANKS_DELAY + 0.3, TIPRANKS_DELAY + 1.8))  # ⏱️ затримка для обходу захисту

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print("✅ TipRanks response:", resp.status_code)

        if resp.status_code != 200 or not resp.text.strip():
            print("❌ Invalid response from TipRanks")
            return None

        if "<html" in resp.text.lower():
            print("❌ HTML detected — response is not JSON")
            return None

        try:
            data = resp.json()
        except json.JSONDecodeError:
            print("💥 Failed to decode JSON")
            return None

        print("📦 Parsed JSON keys:", list(data.keys()))

        stocks = data.get("models", {}).get("stocks", [])
        if not stocks:
            print("❌ No 'stocks' section in JSON")
            return None

        for i in reversed(range(len(stocks))):
            stock = stocks[i]
            smart = stock.get("smartScore")
            if isinstance(smart, dict) and "value" in smart:
                score = smart["value"]
                print(f"📈 Found smartScore in stock[{i}]:", score)
                return {
                    "tipranks_score": float(score),
                    "raw_data": data,
                }

        print("❌ smartScore not found in any stock[] entry")
        return None

    except Exception as e:
        print(f"💥 Exception during TipRanks fetch: {e}")
        return None
