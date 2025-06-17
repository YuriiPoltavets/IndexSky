# SQL schema definition for the stock_metrics table

stock_metrics_schema = """
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
