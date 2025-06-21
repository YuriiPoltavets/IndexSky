import os
import sys
import datetime
from flask import Flask, request
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.form_handler import process_index_form


def _base_data():
    return {
        'rows_count': '1',
        'action': 'data_search',
        'symbol_0': 'AAPL',
        'sector_0': '',
        'zacks_0': '',
        'tipranks_0': '',
        'sector_growth_0': ''
    }


def test_data_search_assigns_row_class_ok():
    app = Flask(__name__)
    data = _base_data()

    with app.test_request_context('/', method='POST', data=data):
        with patch('services.form_handler.get_sector_from_cache', return_value=''), \
             patch('services.form_handler.parse_data') as parse_data_mock, \
             patch('services.form_handler.get_sector_growth', return_value='1%'):
            parse_data_mock.return_value = {
                'Sector': 'Technology',
                'Zacks': 2,
                'TipRanks': 8,
                'Sector Growth': '1%'
            }
            rows = process_index_form(request)

    assert rows[0]['row_class'] == 'ok-blue'


def test_data_search_assigns_row_class_error():
    app = Flask(__name__)
    data = _base_data()

    with app.test_request_context('/', method='POST', data=data):
        with patch('services.form_handler.get_sector_from_cache', return_value=''), \
             patch('services.form_handler.parse_data') as parse_data_mock, \
             patch('services.form_handler.get_sector_growth', return_value='1%'):
            parse_data_mock.return_value = {}
            rows = process_index_form(request)

    assert rows[0]['row_class'] == 'row-error'
