from flask import Blueprint, request, jsonify
from services.user_service import create_user, get_user, delete_user, update_user

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.post("/create")
def create():
    body = request.get_json()

    # try: 
    #     validated = validate(NoteCreateSchema, body)
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 400
    
    note = create_user(body)
    return jsonify({"data": note}), 201




@bp.get("/<user_id>")
def fetch(user_id):
    user = get_user(user_id)
    if not user:
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": user})


@bp.put("/<user_id>")
def update(user_id):
    body = request.get_json()

    user = update_user(user_id, body)
    return jsonify({"data": user})


@bp.delete("/<user_id>")
def delete(user_id):
    delete_user(user_id)
    return jsonify({"success": True}), 204