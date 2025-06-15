import sqlite3
import os

# Path to SQLite database file in project root
DB_PATH = os.path.join(os.path.dirname(__file__), "skyindex.db")

# SQL statement to ensure the table exists
TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS stock_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    zacks_rank_norm REAL,
    date TEXT
);
"""

def save_stock_data(data: dict):
    """Save normalized stock metric data to the database.

    Parameters
    ----------
    data : dict
        Dictionary of column names to values. Keys should correspond to
        columns of the ``stock_metrics`` table. Only normalized values
        should be provided.
    """

    # 1) Open a connection to the SQLite database
    conn = sqlite3.connect(DB_PATH)

    try:
        cur = conn.cursor()

        # 2) Make sure the table exists before inserting
        cur.execute(TABLE_SCHEMA)

        # 3) Build the INSERT statement dynamically from the dict keys
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        sql = f"INSERT INTO stock_metrics ({columns}) VALUES ({placeholders})"

        # 4) Execute the INSERT with parameterized values
        cur.execute(sql, tuple(data.values()))

        # 5) Commit the transaction so changes are saved
        conn.commit()
    finally:
        # 6) Always close the connection
        conn.close()
