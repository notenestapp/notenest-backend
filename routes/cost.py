from flask import Blueprint, request, jsonify
from services.cost_service import get_costt
from utils.limiter import limiter

bp = Blueprint("cost", __name__, url_prefix="/api/cost")


# @bp.get("/")
# def fetchAl():
#     plans = fetchAll()
#     if not plans: 
#         return jsonify({"error": "Not Found"}), 404
#     return jsonify({"data": plans})


@bp.post("/")
@limiter.limit("10 per minute")
def get_cost():
    body = request.get_json()
    data = body['data']
    data = get_costt(data)
    return jsonify({"cost": data}), 200





