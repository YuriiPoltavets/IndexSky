from flask import Blueprint, request, jsonify

from services.fetch_service import build_stock_response

fetch_bp = Blueprint('fetch_bp', __name__)


@fetch_bp.route('/fetch-data', methods=['POST'])
def fetch_data():
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    symbol = payload.get('symbol') if isinstance(payload, dict) else None
    row_index = payload.get('rowIndex') if isinstance(payload, dict) else None
    sector = payload.get('sector') if isinstance(payload, dict) else ""

    if not symbol or not str(symbol).strip():
        return jsonify({"error": "Symbol is required"}), 400

    try:
        result = build_stock_response(symbol, sector=sector, row_index=row_index)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
