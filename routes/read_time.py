from flask import Blueprint, request, jsonify
from services.read_time_service import get_user_read_time, update_user_video_watch_time
from utils.limiter import limiter

bp = Blueprint("read_time", __name__, url_prefix="/api/read_time")

@bp.get("/user/<user_id>")
@limiter.limit("20 per minute")
def get(user_id):
    response = get_user_read_time(user_id)
    
    return jsonify({
        "data": response,
    }), 201


@bp.put("/<any_id>")
@limiter.limit("20 per minute")
def update(any_id):
    data = request.get_json()
    response = update_user_video_watch_time(data=data['data'])

    return jsonify({data: response})

