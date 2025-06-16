import json
import sqlite3
from typing import Any, Dict

from database.database import DB_PATH


TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS stock_metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  symbol TEXT,
  date TEXT,
  open_price REAL,
  close_price REAL,
  price_change_today REAL,
  price_at_parse REAL,
  metrics TEXT,
  UNIQUE(symbol, date)
);
"""


def save_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Insert or update a normalized stock row into the database."""
    symbol = row.get("symbol")
    date = row.get("date")
    if not symbol or not date:
        return {"symbol": symbol, "status": "error", "reason": "missing symbol or date"}

    metrics = row.get("metrics", {})
    if not isinstance(metrics, dict):
        return {"symbol": symbol, "status": "error", "reason": "invalid metrics"}

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(TABLE_SCHEMA)

            sql = (
                "INSERT INTO stock_metrics (symbol, date, open_price, close_price, "
                "price_change_today, price_at_parse, metrics) "
                "VALUES (?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(symbol, date) DO UPDATE SET "
                "open_price=excluded.open_price, "
                "close_price=excluded.close_price, "
                "price_change_today=excluded.price_change_today, "
                "price_at_parse=excluded.price_at_parse, "
                "metrics=excluded.metrics"
            )

            cur.execute(
                sql,
                (
                    symbol,
                    date,
                    row.get("open_price"),
                    row.get("close_price"),
                    row.get("price_change_today"),
                    row.get("price_at_parse"),
                    json.dumps(metrics),
                ),
            )
            conn.commit()
    except Exception as e:
        return {"symbol": symbol, "status": "error", "reason": str(e)}

    return {"symbol": symbol, "status": "ok"}
