import json
import time
import random
import requests
from typing import Dict, Optional, List

from config.delays import TIPRANKS_DELAY
from .base_fetcher import BaseFetcher

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.101 Safari/537.36",
]

_PROXY_LOAD_ERROR = ""

def load_authorized_proxies(path: str = "proxies_auth.json") -> list[dict]:
    global _PROXY_LOAD_ERROR
    try:
        with open(path, "r", encoding="utf-8") as f:
            _PROXY_LOAD_ERROR = ""
            return json.load(f)
    except Exception as e:
        _PROXY_LOAD_ERROR = str(e)
        return []

class TipranksFetcher(BaseFetcher):
    current_ua_index = 0
    proxies = load_authorized_proxies()

    def fetch(self, symbol: str, log_list: Optional[List[str]] = None) -> Dict[str, Optional[float]]:
        if not symbol:
            return {"tipranks": None}

        symbol = symbol.strip().lower()
        print(f"\n🔎 TipRanks for symbol: {symbol.upper()}")

        if not self.proxies:
            if log_list is not None and _PROXY_LOAD_ERROR:
                log_list.append(f"{symbol} ❌ Не вдалося завантажити авторизовані проксі: {_PROXY_LOAD_ERROR}")
            return {"tipranks": None}

        for attempt in range(len(USER_AGENTS)):
            user_agent = USER_AGENTS[TipranksFetcher.current_ua_index]
            proxy_info = random.choice(self.proxies)

            proxy_url = f"http://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['ip']}:{proxy_info['port']}"
            proxy_dict = {
                "http": proxy_url,
                "https": proxy_url,
            }

            headers = {
                "User-Agent": user_agent,
                "Accept": "application/json",
                "Referer": f"https://www.tipranks.com/stocks/{symbol}/stock-analysis",
            }

            print(f"🌐 Proxy: {proxy_info['ip']}:{proxy_info['port']} | UA: {user_agent}")

            time.sleep(TIPRANKS_DELAY)

            try:
                response = requests.get(
                    f"https://www.tipranks.com/stocks/{symbol}/stock-analysis/payload.json",
                    headers=headers,
                    proxies=proxy_dict,
                    timeout=5,
                )
                print(f"✅ Response: {response.status_code} | UA index: {self.current_ua_index}")

                if response.status_code != 200 or not response.text.strip():
                    return {"tipranks": None}

                if "<html" in response.text.lower():
                    if log_list is not None:
                        log_list.append(f"{symbol} ⚠️ Отримано HTML замість JSON")
                    self.current_ua_index = (self.current_ua_index + 1) % len(USER_AGENTS)
                    continue

                try:
                    data = response.json()
                    print("📦 JSON розпарсено")
                except json.JSONDecodeError:
                    if log_list is not None:
                        log_list.append(f"{symbol} ❌ JSON помилка")
                    return {"tipranks": None}

                stocks = data.get("models", {}).get("stocks", [])
                for stock in reversed(stocks):
                    smart = stock.get("smartScore")
                    if isinstance(smart, dict) and "value" in smart:
                        score = smart["value"]
                        if isinstance(score, (int, float)):
                            print(f"🎯 SmartScore знайдено: {score}")
                            return {"tipranks": float(score)}

                if log_list is not None:
                    log_list.append(f"{symbol} ⚠️ SmartScore не знайдено")
                return {"tipranks": None}

            except Exception as e:
                print(f"💥 Виняток: {e}")
                self.current_ua_index = (self.current_ua_index + 1) % len(USER_AGENTS)
                continue

        print("⛔ Всі спроби з UA вичерпані")
        return {"tipranks": None}

fetch_tipranks_data = TipranksFetcher().fetch
