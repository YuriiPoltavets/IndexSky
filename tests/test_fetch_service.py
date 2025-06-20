import os
import sys
import datetime
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.fetch_service import build_stock_response
from services.metrics_cache import metrics_cache


def test_build_stock_response_caches_metrics():
    metrics_cache.clear()
    today = datetime.date.today().strftime('%Y-%m-%d')

    with patch('services.fetch_service.fetcher_manager') as fm, \
         patch('services.fetch_service.get_sector_from_cache', return_value='Technology'), \
         patch('services.fetch_service.get_sector_yf', return_value='Technology'), \
         patch('services.fetch_service.get_sector_growth', return_value='1%'):
        fm.fetch_all.return_value = {'zacks': '2', 'tipranks': 9, 'row_class': 'row-ok'}
        result = build_stock_response('aapl', row_index=1)

    assert result['zacks'] == 2
    assert result['tipranks'] == 9
    assert result['sector'] == 'Technology'
    assert result['sector_growth'] == '1%'
    assert result['row_class'] == 'row-ok'
    assert result['rowIndex'] == 1
    assert metrics_cache['AAPL']['zacks'] == 2
    assert metrics_cache['AAPL']['tipranks'] == 9
    assert metrics_cache['AAPL']['date'] == today
