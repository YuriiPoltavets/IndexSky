from flask import Blueprint, render_template, request

from services.form_handler import (
    process_index_form,
    sector_growth_loaded,
)
from config.constants import HEADERS, SECTOR_OPTIONS

index_bp = Blueprint('index_bp', __name__)


@index_bp.route('/', methods=['GET', 'POST'])
def index():
    rows = process_index_form(request)
    logs: list[str] = []
    if request.method == "POST" and request.form.get("action") == "data_search":
        if sector_growth_loaded:
            logs.append("✅ Sector Growth loaded")
        else:
            logs.append("⚠️ Sector Growth failed to load")
    return render_template(
        'index.html',
        headers=HEADERS,
        rows=rows,
        sectors=SECTOR_OPTIONS,
        sector_growth_loaded=sector_growth_loaded,
        logs=logs,
    )
