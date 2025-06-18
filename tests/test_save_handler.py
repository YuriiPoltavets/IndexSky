import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from logic.save_handler import save_row


def _mock_connection():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = False
    return mock_conn, mock_cursor


def test_valid_row_inserts_to_db():
    row = {
        "symbol": "AAPL",
        "date": "2025-06-18",
        "metrics": {"zacks_rank_norm": 0.5},
    }
    mock_conn, mock_cursor = _mock_connection()

    with patch("logic.save_handler.sqlite3.connect", return_value=mock_conn) as mock_connect:
        result = save_row(row)

    assert result == {"symbol": "AAPL", "status": "ok"}
    mock_connect.assert_called_once()
    mock_conn.commit.assert_called_once()

    insert_sql = (
        "INSERT INTO stock_metrics (symbol, date, open_price, close_price, "
        "price_change_today, price_at_parse, skyindex_score, metrics, is_etf) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    metrics_json = json.dumps(row["metrics"])
    mock_cursor.execute.assert_any_call(
        insert_sql,
        (
            row["symbol"],
            row["date"],
            None,
            None,
            None,
            None,
            None,
            metrics_json,
            None,
        ),
    )


def test_missing_symbol_returns_error():
    row = {
        "date": "2025-06-18",
        "metrics": {"zacks_rank_norm": 0.5},
    }
    with patch("logic.save_handler.sqlite3.connect") as mock_connect:
        result = save_row(row)
    assert result["status"] == "error"
    mock_connect.assert_not_called()


def test_missing_date_returns_error():
    row = {
        "symbol": "AAPL",
        "metrics": {"zacks_rank_norm": 0.5},
    }
    with patch("logic.save_handler.sqlite3.connect") as mock_connect:
        result = save_row(row)
    assert result["status"] == "error"
    mock_connect.assert_not_called()


def test_invalid_metrics_returns_error():
    row = {
        "symbol": "AAPL",
        "date": "2025-06-18",
        "metrics": "notadict",
    }
    with patch("logic.save_handler.sqlite3.connect") as mock_connect:
        result = save_row(row)
    assert result["status"] == "error"
    mock_connect.assert_not_called()
