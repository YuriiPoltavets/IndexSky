import os
import sys
import datetime
from flask import Flask, request
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.form_handler import process_index_form
from services.metrics_cache import metrics_cache


def test_process_index_form_calculate_uses_cache():
    app = Flask(__name__)
    metrics_cache.clear()
    today = datetime.date.today().strftime('%Y-%m-%d')
    metrics_cache['AAPL'] = {
        'symbol': 'AAPL',
        'zacks': 1,
        'tipranks': 8,
        'sector': 'Technology',
        'date': today
    }

    data = {
        'rows_count': '1',
        'action': 'calculate',
        'symbol_0': 'AAPL',
        'sector_0': 'Technology',
        'zacks_0': '',
        'tipranks_0': '',
        'sector_growth_0': '1%'
    }

    with app.test_request_context('/', method='POST', data=data):
        with patch('services.form_handler.add_sector') as add_sector, \
             patch('services.form_handler.get_sector_growth', return_value='1%'), \
             patch('services.form_handler.get_sector_growth_data', return_value={'3d': '2', '7d': '3'}), \
             patch('services.form_handler.normalize_row') as normalize_row, \
             patch('services.form_handler.save_row', return_value={'status': 'ok'}):
            normalize_row.return_value = {
                'symbol': 'AAPL',
                'date': today,
                'metrics': {},
                'skyindex_score': 0.5
            }
            rows = process_index_form(request)

    assert rows[0]['skyindex_score'] == 0.5
    assert rows[0]['row_class'] == 'row-ok'
    normalize_row.assert_called()
    add_sector.assert_called_once_with('AAPL', 'Technology')

