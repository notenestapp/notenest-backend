from flask import Blueprint, request, jsonify, current_app
from services.chapters_service import create_chapter, get_chapter, query_chapters, update_chapter, delete_chapter, fetchAll, generate_chapter
from utils.limiter import limiter
bp = Blueprint("chapters", __name__, url_prefix="/api/chapters")



@bp.get("/")
def get_chapters():
    filters = request.args.to_dict()
    data = query_chapters(filters)
    return {"data": data}, 200




@bp.post("/create")
@limiter.limit("10 per minute")
def create():
    body = request.get_json()

    # try: 
    #     validated = validate(NoteCreateSchema, body)
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 400
    
    note = create_chapter(body)
    return jsonify({"data": note}), 201



from werkzeug.exceptions import ClientDisconnected

@bp.post("/generate")
@limiter.limit("5 per minute")
def generate():
    try:
        current_app.logger.info("Generate endpoint called")

        if not request.content_type or not request.content_type.startswith("multipart/form-data"):
            return jsonify({"error": "Invalid content type"}), 400

        note_id = request.form.get("note_id")
        user_id = request.form.get("user_id")
        if not note_id:
            return jsonify({"error": "note_id missing"}), 400

        files_obj = request.files.getlist("files")
        if not files_obj:
            return jsonify({"error": "No files uploaded"}), 400

        current_app.logger.info(
            "Files received: %s",
            [f.filename for f in files_obj]
        )

        response = generate_chapter(note_id, user_id, files_obj)
        return jsonify({"data": response})

    except ClientDisconnected:
        current_app.logger.warning("Client disconnected during upload")
        return jsonify({"error": "Upload interrupted"}), 400

    except Exception as e:
        current_app.logger.exception("Unhandled exception in generate endpoint")
        return jsonify({"error": "Internal server error"}), 500


@bp.get("/user/<user_id>")
@limiter.limit("10 per minute")
def fetchAl(user_id):
    chapters = fetchAll(user_id)
    if not chapters: 
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": chapters})


@bp.get("/<chapter_id>")
@limiter.limit("10 per minute")
def fetch(chapter_id):
    print("Getting Chapter")
    chapter = get_chapter(chapter_id)
    if not chapter:
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": chapter})


@bp.put("/<chapter_id>")
@limiter.limit("10 per minute")
def update(chapter_id):
    body = request.get_json()

    chapter = update_chapter(chapter_id, body)
    return jsonify({"data": chapter})


@bp.delete("/<chapter_id>")
@limiter.limit("10 per minute")
def delete(chapter_id):
    delete_chapter(chapter_id)
    return jsonify({"success": True}), 204