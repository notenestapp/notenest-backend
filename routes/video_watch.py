from flask import Blueprint, request, jsonify
from services.video_watch_service import get_user_video_watch_time, update_user_video_watch_time
from utils.limiter import limiter

bp = Blueprint("video_watch", __name__, url_prefix="/api/video_watch")

@bp.get("/user/<user_id>")
@limiter.limit("20 per minute")
def get(user_id):

    response = get_user_video_watch_time(user_id)
    
    return jsonify({
        "data": response,
    }), 201



@bp.put("/<any_id>")
@limiter.limit("20 per minute")
def update():
    data = request.get_json()

    response = update_user_video_watch_time(data=data)

    return jsonify({data: response})


