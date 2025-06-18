import json
import time
from typing import Dict, Optional
import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
)

def fetch_tipranks_data(symbol: str, delay_sec: float = 0.8) -> Optional[Dict]:
    """Return TipRanks Smart Score from payload.json endpoint, scanning stocks[] from end."""
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

    try:
        time.sleep(delay_sec)  # avoid rate-limiting

        resp = requests.get(url, headers=headers, timeout=10)
        print("✅ TipRanks response:", resp.status_code)
        if resp.status_code != 200 or not resp.text.strip():
            print("❌ Empty or bad response body")
            return None

        data = resp.json()
        print("📦 Parsed JSON keys:", list(data.keys()))

        stocks = data.get("models", {}).get("stocks", [])
        if not stocks:
            print(f"❌ No stocks[] in JSON for {symbol.upper()}")
            return None

        score = None
        for i in range(len(stocks) - 1, -1, -1):  # ← scan from end
            print(f"🔍 Checking stock[{i}]...")
            smart = stocks[i].get("smartScore")
            if smart and isinstance(smart, dict) and "value" in smart:
                score = smart["value"]
                print(f"📈 Found smartScore in stock[{i}]:", score)
                break

        if score is None:
            print(f"❌ smartScore not found in any stock[] for {symbol.upper()}")
            return None

        return {
            "tipranks_score": float(score),
            "raw_data": data,
        }

    except json.JSONDecodeError:
        print(f"💥 Failed to decode JSON from TipRanks for {symbol.upper()}")
        return None
    except Exception as e:
        print(f"💥 Exception during TipRanks fetch for {symbol.upper()}: {str(e)}")
        return None
