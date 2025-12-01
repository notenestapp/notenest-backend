from flask import Blueprint, request, jsonify
from services.files_service import upload_file, delete_file, get_file_url

bp = Blueprint("files", __name__, url_prefix="/files")

@bp.post("/upload")
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file_obj = request.files["file"]
    saved = upload_file(file_obj)

    url = get_file_url(saved["$id"])
    return jsonify({
        "fileId": saved["$id"],
        "url": url
    })

@bp.delete("/<file_id>")
def remove(file_id):
    delete_file(file_id)
    return jsonify({"status": "deleted"})
