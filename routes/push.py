from flask import Blueprint, request, jsonify
from services.push_service import create_token

bp = Blueprint("push", __name__, url_prefix="/api/push")

@bp.post("/register")
def register_push_token():
    data = request.get_json()
    token = data.get("token")
    platform = data.get("platform")
    user_id = data.get("user_id")

    if not token or not platform:
        return jsonify({"error": "token and platform are required"}), 400

    new_token = create_token(
        user_id=user_id,
        token=token,
        platform=platform,
        is_active=True
    )

    return jsonify({"message": "Token registered successfully"}), 201
