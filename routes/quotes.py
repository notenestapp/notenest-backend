from flask import Blueprint, request, jsonify
from services.qoutes_service import create_quote, fetchAll, query_quotes, update_quote, delete_quote, get_quote
from utils.limiter import limiter


bp = Blueprint("quotes", __name__, url_prefix="/api/quotes")

@bp.post("/create")
@limiter.limit("10 per minute")
def create():
    body = request.get_json()

    # try: 
    #     validated = validate(NoteCreateSchema, body)
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 400
    
    quote = create_quote(body['data'])
    return jsonify({"data": quote}), 201


@bp.get("/")
@limiter.limit("10 per minute")
def get_quotes():
    filters = request.args.to_dict()
    data = query_quotes(filters)
    return {"data": data}, 200



@bp.get("/user/<user_id>")
@limiter.limit("10 per minute")
def fetchAl(user_id):
    quote = fetchAll(user_id)
    if not quote: 
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": quote})


@bp.get("/<quote_id>")
@limiter.limit("10 per minute")
def fetch(quote_id):
    quote = get_quote(quote_id)
    if not quote:
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": quote})


@bp.put("/<quote_id>")
@limiter.limit("10 per minute")
def update(quote_id):
    body = request.get_json()

    quote = update_quote(quote_id, body['data'])
    return jsonify({"data": quote})


@bp.delete("/<quote_id>")
@limiter.limit("10 per minute")
def delete(quote_id):
    delete_quote(quote_id)
    return jsonify({"success": True}), 204