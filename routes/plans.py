from flask import Blueprint, request, jsonify
from services.plans_service import get_plan, fetchAll,query_plans
from utils.limiter import limiter

bp = Blueprint("plans", __name__, url_prefix="/api/plans")


# @bp.get("/")
# def fetchAl():
#     plans = fetchAll()
#     if not plans: 
#         return jsonify({"error": "Not Found"}), 404
#     return jsonify({"data": plans})


@bp.get("/")
@limiter.limit("10 per minute")
def get_plans():
    filters = request.args.to_dict()
    print("FILTERS: ", filters)
    data = query_plans(filters)
    print("Data: ", data)
    return jsonify({"data": data}), 200



@bp.get("/<plan_id>")
@limiter.limit("10 per minute")
def fetch(plan_id):
    plan = get_plan(plan_id)
    print("Plan: ", plan)
    if not plan:
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": plan})

