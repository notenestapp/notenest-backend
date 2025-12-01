from flask import Blueprint, request, jsonify
from services.subscriptions_service import create_subscription, delete_subscription, fetchAll, get_subscription, update_subscription


bp = Blueprint("subscriptions", __name__, url_prefix="/subscriptions")

@bp.post("/create")
def create():
    body = request.get_json()

    # try: 
    #     validated = validate(NoteCreateSchema, body)
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 400
    
    note = create_subscription(body)
    return jsonify({"data": note}), 201


@bp.get("/user/<user_id>")
def fetchAl(user_id):
    subscriptions = fetchAll(user_id)
    if not subscriptions: 
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": subscriptions})


@bp.get("/<subscription_id>")
def fetch(subscription_id):
    note = get_subscription(subscription_id)
    if not note:
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": note})


@bp.put("/<subscription_id>")
def update(subscription_id):
    body = request.get_json()

    note = update_subscription(subscription_id, body)
    return jsonify({"data": note})


@bp.delete("/<subscription_id>")
def delete(subscription_id):
    delete_subscription(subscription_id)
    return jsonify({"success": True}), 204