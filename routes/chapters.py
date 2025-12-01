from flask import Blueprint, request, jsonify
from services.chapters_service import create_chapter, get_chapter, query_chapters, update_chapter, delete_chapter, fetchAll

bp = Blueprint("chapters", __name__, url_prefix="/chapters")



@bp.get("/")
def get_chapters():
    filters = request.args.to_dict()
    print("FILTERS: ", filters)
    data = query_chapters(filters)
    return {"data": data}, 200




@bp.post("/create")
def create():
    body = request.get_json()

    # try: 
    #     validated = validate(NoteCreateSchema, body)
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 400
    
    note = create_chapter(body)
    return jsonify({"data": note}), 201


@bp.get("/user/<user_id>")
def fetchAl(user_id):
    chapters = fetchAll(user_id)
    if not chapters: 
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": chapters})


@bp.get("/<chapter_id>")
def fetch(chapter_id):
    chapter = get_chapter(chapter_id)
    if not chapter:
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": chapter})


@bp.put("/<chapter_id>")
def update(chapter_id):
    body = request.get_json()

    chapter = update_chapter(chapter_id, body)
    return jsonify({"data": chapter})


@bp.delete("/<chapter_id>")
def delete(chapter_id):
    delete_chapter(chapter_id)
    return jsonify({"success": True}), 204