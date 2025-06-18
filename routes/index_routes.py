from flask import Blueprint, render_template, request

from services.form_handler import (
    process_index_form,
    HEADERS,
    SECTOR_OPTIONS,
    sector_growth_loaded,
)

index_bp = Blueprint('index_bp', __name__)


@index_bp.route('/', methods=['GET', 'POST'])
def index():
    rows = process_index_form(request)
    return render_template(
        'index.html',
        headers=HEADERS,
        rows=rows,
        sectors=SECTOR_OPTIONS,
        sector_growth_loaded=sector_growth_loaded,
    )
