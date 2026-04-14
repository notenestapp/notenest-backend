from flask import Blueprint, request, jsonify
from services.push_service import create_token, send_push_notification

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


@bp.post("/send")
def send_push_notification_route():
    data = request.get_json()
    user_id = data.get("user_id")
    title = data.get("title")
    body = data.get("body")
    data = data.get("data")

    if not user_id or not title or not body:
        return jsonify({"error": "user_id, title and body are required"}), 400

    send_push_notification(user_id=user_id, title=title, body=body, data=data)

    return jsonify({"message": "Push notification sent successfully"}), 200


# def notify_user(payload: dict, authorization: str = Header(None)):
#     if authorization != f"Bearer {os.getenv('INTERNAL_API_KEY')}":
#         raise HTTPException(status_code=403, detail="Unauthorized")

#     user_id = payload.get("user_id")
#     title = payload.get("title")
#     body = payload.get("body")

#     if not user_id:
#         raise HTTPException(status_code=400, detail="Missing user_id")

#     send_push_notification(user_id, title, body)

#     return {"success": True}