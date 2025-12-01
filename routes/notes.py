from flask import Blueprint, request, jsonify
from services.notes_service import create_note, get_note, delete_note, update_note, fetchAll

bp = Blueprint("notes", __name__, url_prefix="/notes")

@bp.post("/create")
def create():
    body = request.get_json()

    # try: 
    #     validated = validate(NoteCreateSchema, body)
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 400
    
    note = create_note(body)
    return jsonify({"data": note}), 201


@bp.get("/user/<user_id>")
def fetchAl(user_id):
    notes = fetchAll(user_id)
    if not notes: 
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": notes})


@bp.get("/<note_id>")
def fetch(note_id):
    note = get_note(note_id)
    if not note:
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": note})


@bp.put("/<note_id>")
def update(note_id):
    body = request.get_json()

    note = update_note(note_id, body)
    return jsonify({"data": note})


@bp.delete("/<note_id>")
def delete(note_id):
    delete_note(note_id)
    return jsonify({"success": True}), 204