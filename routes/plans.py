from flask import Blueprint, request, jsonify
from services.plans_service import get_plan, fetchAll

bp = Blueprint("plans", __name__, url_prefix="/plans")


@bp.get("/")
def fetchAl():
    plans = fetchAll()
    if not plans: 
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": plans})


@bp.get("/<plan_id>")
def fetch(plan_id):
    plan = get_plan(plan_id)
    if not plan:
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": plan})

