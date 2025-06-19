import json
import time
import requests
from typing import Dict, Optional

from config.delays import TIPRANKS_DELAY
from .base_fetcher import BaseFetcher

# 🔁 Актуальні десктопні User-Agent'и (2024–2025)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.101 Safari/537.36",
]

class TipranksFetcher(BaseFetcher):
    """Retrieve SmartScore from TipRanks."""

    current_ua_index = 0  # індекс активного UA

    def fetch(self, symbol: str) -> Dict[str, Optional[float]]:
        """Return the TipRanks SmartScore for the given stock symbol."""
        if not symbol:
            return {"tipranks": None}

        symbol = symbol.strip().lower()
        print(f"\n🔎 TipRanks for symbol: {symbol.upper()}")

        for attempt in range(len(USER_AGENTS)):
            user_agent = USER_AGENTS[TipranksFetcher.current_ua_index]
            headers = {
                "User-Agent": user_agent,
                "Accept": "application/json",
                "Referer": f"https://www.tipranks.com/stocks/{symbol}/stock-analysis",
            }

            time.sleep(TIPRANKS_DELAY)

            try:
                response = requests.get(
                    f"https://www.tipranks.com/stocks/{symbol}/stock-analysis/payload.json",
                    headers=headers,
                    timeout=10,
                )
                print(f"✅ TipRanks response: {response.status_code} | UA index: {TipranksFetcher.current_ua_index}")

                if response.status_code != 200 or not response.text.strip():
                    return {"tipranks": None}

                if "<html" in response.text.lower():
                    print("⚠️ Received HTML instead of JSON — switching User-Agent")
                    TipranksFetcher.current_ua_index = (TipranksFetcher.current_ua_index + 1) % len(USER_AGENTS)
                    continue  # пробуємо з новим UA

                try:
                    data = response.json()
                    print("📦 TipRanks JSON loaded")
                except json.JSONDecodeError:
                    print("❌ Failed to parse JSON")
                    return {"tipranks": None}

                stocks = data.get("models", {}).get("stocks", [])
                for stock in reversed(stocks):
                    smart = stock.get("smartScore")
                    if isinstance(smart, dict) and "value" in smart:
                        score = smart["value"]
                        if isinstance(score, (int, float)):
                            print(f"🎯 TipRanks SmartScore FOUND: {score}")
                            return {"tipranks": float(score)}

                print("⚠️ SmartScore not found in any stock")
                return {"tipranks": None}

            except Exception as e:
                print(f"💥 Exception during TipRanks fetch: {e}")
                return {"tipranks": None}

        print("⛔ All User-Agents failed")
        return {"tipranks": None}


# Backward-compatible alias
fetch_tipranks_data = TipranksFetcher().fetch
