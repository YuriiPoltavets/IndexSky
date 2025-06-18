import sqlite3
import os

from .schema import stock_metrics_schema

# Path to SQLite database file in project root
DB_PATH = os.path.join(os.path.dirname(__file__), "skyindex.db")

# SQL statement to ensure the table exists
TABLE_SCHEMA = stock_metrics_schema

