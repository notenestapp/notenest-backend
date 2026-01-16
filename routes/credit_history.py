from flask import Blueprint, request, jsonify
from services.credit_history_service import create_credit_record, get_credit_history
from utils.limiter import limiter

# filepath: c:\Users\hp\Desktop\Projects\HACKATHON\flask_test\notenest-backend\routes\credit_history.py

bp = Blueprint("credit-history", __name__, url_prefix="/api/credit-history")


@bp.post("/create")
@limiter.limit("10 per minute")
def create():
    body = request.get_json()
    
    record = create_credit_record(body['data'])
    return jsonify({"data": record[0]}), record[1]


@bp.get("/<user_id>")
@limiter.limit("10 per minute")
def fetch(user_id):
    history = get_credit_history(user_id)
    if not history:
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": history}), 200