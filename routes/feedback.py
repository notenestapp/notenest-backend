from flask import Blueprint, request, jsonify
from services.feedbacks_service import create_feedback

bp = Blueprint("notes", __name__, url_prefix="/notes")

@bp.post("/create")
def create():
    body = request.get_json()

    # try: 
    #     validated = validate(NoteCreateSchema, body)
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 400
    
    feedback = create_feedback(body)
    return jsonify({"data": feedback}), 201


