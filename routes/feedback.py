from flask import Blueprint, request, jsonify
from utils.limiter import limiter
from services.feedbacks_service import create_feedback

bp = Blueprint("feedback", __name__, url_prefix="/api/feedback")

@bp.post("/create")
@limiter.limit("10 per minute")
def create():
    body = request.get_json()

    
    feedback = create_feedback(body)
    return jsonify({"data": feedback}), 201


