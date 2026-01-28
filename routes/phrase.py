from flask import Blueprint, request, jsonify
from services.phrase_service import getPhrase
from utils.limiter import limiter

bp = Blueprint("phrase", __name__, url_prefix="/api/phrase")

@bp.get("/get_phrase")
@limiter.limit("10 per minute")
def get_phrase():
    try:
        phrase = getPhrase()


        return jsonify({"data": phrase}), 200
    except: 
        print("Errror")


