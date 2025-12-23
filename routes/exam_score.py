from flask import Blueprint, request, jsonify
from services.exam_score_service import get_user_exam_score
from utils.limiter import limiter

bp = Blueprint("exam_score", __name__, url_prefix="/api/exam_score")

@bp.get("/user/<user_id>")
@limiter.limit("20 per minute")
def get(user_id):

    response = get_user_exam_score(user_id)
    
    return jsonify({
        "data": response,
    }), 201


