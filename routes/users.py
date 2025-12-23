from flask import Blueprint, request, jsonify
from services.user_service import create_user, get_user, delete_user, update_user, query_users, add_streak, reset_streak
from utils.limiter import limiter

bp = Blueprint("users", __name__, url_prefix="/api/users")

@bp.post("/create")
@limiter.limit("10 per minute")
def create():
    body = request.get_json()

    # try: 
    #     validated = validate(NoteCreateSchema, body)
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 400
    
    note = create_user(body['data'])
    return jsonify(note), 201



@bp.get("/")
@limiter.limit("10 per minute")
def get_chapters():
    
    filters = request.args.to_dict()
    print("FILTERS: ", filters)
    data = query_users(filters)
    return {"data": data}, 200

@bp.get("/streak/add/<user_id>")
@limiter.limit("10 per minute")
def add(user_id):

    response = add_streak(user_id=user_id)
    return {"data": response}, 200



@bp.get("/streak/reset/<user_id>")
@limiter.limit("10 per minute")
def reset(user_id):

    response = reset_streak(user_id=user_id)
    return {"data": response}, 200



@bp.get("/<user_id>")
@limiter.limit("10 per minute")
def fetch(user_id):
    user = get_user(user_id)
    if not user:
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": user})


@bp.put("/<user_id>")
@limiter.limit("10 per minute")
def update(user_id):
    body = request.get_json()
    data = body['data']
    dataa = data['data']

    user = update_user(user_id, dataa)
    return jsonify({"data": user})


@bp.delete("/<user_id>")
@limiter.limit("10 per minute")
def delete(user_id):
    delete_user(user_id)
    return jsonify({"success": True}), 204