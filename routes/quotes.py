from flask import Blueprint, request, jsonify
from services.qoutes_service import create_quote, fetchAll, query_quotes, update_quote, delete_quote, get_quote

bp = Blueprint("quotes", __name__, url_prefix="/quotes")

@bp.post("/create")
def create():
    body = request.get_json()

    # try: 
    #     validated = validate(NoteCreateSchema, body)
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 400
    
    quote = create_quote(body)
    return jsonify({"data": quote}), 201


@bp.get("/")
def get_quotes():
    filters = request.args.to_dict()
    print("FILTERS: ", filters)
    data = query_quotes(filters)
    return {"data": data}, 200



@bp.get("/user/<user_id>")
def fetchAl(user_id):
    quote = fetchAll(user_id)
    if not quote: 
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": quote})


@bp.get("/<quote_id>")
def fetch(quote_id):
    quote = get_quote(quote_id)
    if not quote:
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": quote})


@bp.put("/<quote_id>")
def update(quote_id):
    body = request.get_json()

    quote = update_quote(quote_id, body)
    return jsonify({"data": quote})


@bp.delete("/<quote_id>")
def delete(quote_id):
    delete_quote(quote_id)
    return jsonify({"success": True}), 204