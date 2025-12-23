from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        # If it's an HTTPException, use its code/text
        if isinstance(error, HTTPException):
            response = {
                "error": error.name,
                "message": error.description,
                "status": error.code
            }
            return jsonify(response), error.code

        # Otherwise, it's some random Python error
        response = {
            "error": "InternalServerError",
            "message": str(error),
            "status": 500
        }
        print(response)
        return jsonify(response), 500
