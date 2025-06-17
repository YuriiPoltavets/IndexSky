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
  skyindex_score REAL,
  metrics TEXT,
  is_etf INTEGER DEFAULT NULL,
  UNIQUE(symbol, date)
);
"""


def save_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Insert or update a normalized stock row in ``stock_metrics``.

    The ``symbol`` and ``date`` pair acts as a unique key. If a row with the
    same values already exists, all metric columns including ``skyindex_score``
    are updated instead of creating a duplicate.
    """
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

            # Check if a row already exists with the same symbol and date
            cur.execute(
                "SELECT 1 FROM stock_metrics WHERE symbol=? AND date=? LIMIT 1",
                (symbol, date),
            )
            exists = cur.fetchone() is not None

            if exists:
                # Remove the existing row to mimic UPSERT behaviour
                cur.execute(
                    "DELETE FROM stock_metrics WHERE symbol=? AND date=?",
                    (symbol, date),
                )

            insert_sql = (
                "INSERT INTO stock_metrics (symbol, date, open_price, close_price, "
                "price_change_today, price_at_parse, skyindex_score, metrics, is_etf) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            )

            cur.execute(
                insert_sql,
                (
                    symbol,
                    date,
                    row.get("open_price"),
                    row.get("close_price"),
                    row.get("price_change_today"),
                    row.get("price_at_parse"),
                    row.get("skyindex_score"),
                    json.dumps(metrics),
                    row.get("is_etf"),
                ),
            )
            conn.commit()
    except Exception as e:
        return {"symbol": symbol, "status": "error", "reason": str(e)}

    return {"symbol": symbol, "status": "ok"}
