from flask import Blueprint, request, jsonify, current_app
from utils.limiter import limiter
from services.exam_service import create_exam, delete_exam, fetchAll, get_exam, update_exam, fetch_exam_stats

bp = Blueprint("exam", __name__, url_prefix="/api/exam")

@bp.post("/create")
@limiter.limit("10 per minute")
def create():

    current_app.logger.info("Generate endpoint called")

    # if not request.content_type or not request.content_type.startswith("multipart/form-data"):
    #     return jsonify({"error": "Invalid content type"}), 400

    note_id = request.form.get("note_id")
    user_id = request.form.get("user_id")
    no_of_questions = request.form.get("no_of_questions")
    chapter_id = request.form.get("chapter_id")


    files_obj = request.files.getlist("files")
    # if not files_obj:
    #     return jsonify({"error": "No files uploaded"}), 400

    print(user_id, note_id, chapter_id, no_of_questions, files_obj)

    # current_app.logger.info(
    #     "Files received: %s",
    #     [f.filename for f in files_obj]
    # )

    
    exam = create_exam({"note_id": note_id, "user_id": user_id, "no_of_questions": no_of_questions, "chapter_id": chapter_id, "files": files_obj})
    return jsonify({"data": exam}), 201



@bp.get("/<exam_id>")
@limiter.limit("10 per minute")
def get_doc(exam_id):

    exam = get_exam(exam_id)
    return jsonify({"data": exam}), 201



@bp.get("user/<user_id>")
@limiter.limit("10 per minute")
def get_by_user(user_id):

    
    exams = fetchAll(user_id)
    return jsonify({"data": exams}), 201

@bp.get("fetch_latest/user/<user_id>")
@limiter.limit("10 per minute")
def fetch_latest(user_id):

    
    exams = fetch_exam_stats(user_id)
    return jsonify({"data": exams}), 201

@bp.put("/<exam_id>")
@limiter.limit("10 per minute")
def update(exam_id):
    body = request.get_json()

    exam = update_exam(exam_id, body['data'])
    return jsonify({"data": exam})


@bp.delete("/<exam_id>")
@limiter.limit("10 per minute")
def delete(exam_id):
    delete_exam(exam_id)
    return jsonify({"success": True}), 204