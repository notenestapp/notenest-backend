from flask import Blueprint, request, jsonify
from services.notes_service import create_note, get_note, delete_note, update_note, fetchAll
from utils.limiter import limiter

bp = Blueprint("notes", __name__, url_prefix="/api/notes")

@bp.post("/create")
@limiter.limit("10 per minute")
def create():
    body = request.get_json()

    # try: 
    #     validated = validate(NoteCreateSchema, body)
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 400
    
    note = create_note(body['data'])
    print("Result: ", note)
    return jsonify({"data": note}), 201


@bp.get("/user/<user_id>")
@limiter.limit("10 per minute")
def fetchAl(user_id):
    notes = fetchAll(user_id)
    if not notes: 
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": notes})


@bp.get("/<note_id>")
@limiter.limit("10 per minute")
def fetch(note_id):
    note = get_note(note_id)
    if not note:
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": note})


@bp.put("/<note_id>")
@limiter.limit("10 per minute")
def update(note_id):
    body = request.get_json()

    note = update_note(note_id, body['data'])
    return jsonify({"data": note})


@bp.delete("/<note_id>")
@limiter.limit("10 per minute")
def delete(note_id):
    response = delete_note(note_id)
    print("Response: ", )
    return jsonify({"success": response}), 204