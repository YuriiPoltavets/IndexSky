import os
import sys
from math import tanh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logic.normalization import normalize_row


def test_normalize_row_includes_tipranks():
    row = {
        "Symbol": "AAPL",
        "Sector": "Technology",
        "Zacks": "2",
        "TipRanks": "8",
        "sector_growth_1d": "",
        "sector_growth_3d": "",
        "sector_growth_7d": "",
        "Дата": "2025-06-18",
    }
    normalized = normalize_row(row)
    assert normalized is not None
    metrics = normalized["metrics"]
    assert metrics["tipranks_score_norm"] == round(tanh((8 - 5) / 2.0), 4)
    expected_zacks = 0.5
    expected_tip = round(tanh((8 - 5) / 2.0), 4)
    expected_score = round(0.5 * expected_zacks + 0.5 * expected_tip, 4)
    assert normalized["skyindex_score"] == expected_score


def test_normalize_row_handles_missing_tipranks():
    row = {
        "Symbol": "AAPL",
        "Sector": "Technology",
        "Zacks": "2",
        "sector_growth_1d": "",
        "sector_growth_3d": "",
        "sector_growth_7d": "",
        "Дата": "2025-06-18",
    }
    normalized = normalize_row(row)
    assert normalized is not None
    assert normalized["metrics"].get("tipranks_score_norm") is None
