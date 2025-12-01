from flask import Blueprint, request, jsonify, render_template
from services.payments_service import create_payment, fetchAll, update_payment, delete_payment, get_payment, init_payment, payment_callback


bp = Blueprint("payments", __name__, url_prefix="/payments")

@bp.post("/create")
def create():
    body = request.get_json()

    # try: 
    #     validated = validate(NoteCreateSchema, body)
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 400
    
    payment = create_payment(body)
    return jsonify({"data": payment}), 201


@bp.post("/initialize")
def initialize_payment():
    data = request.get_json()

    response = init_payment(data)
    return jsonify({"data": response}), 201


@bp.post("/callback")
def callback():
    reference = request.args.get("reference")
    transactionId = request.args.get('transactionId')
    # accept both variants (snake_case or camelCase) that might be present
    payment_type = request.args.get("payment_type") or request.args.get("paymentType")
    payment_title = request.args.get("payment_title")
    lasting = request.args.get("lasting")
    user_id = request.args.get('user_id')
    credits =request.args.get('credits')
    user_credits = request.args.get('user_credits')

    response = payment_callback({
        "reference": reference,
        "transactionId": transactionId,
        "payment_type": payment_type,
        "payment_title": payment_title,
        "lasting": lasting,
        "user_id": user_id,
        "credits": credits,
        "user_credits": user_credits,
    })

    return render_template(response)



@bp.get("/user/<user_id>")
def fetchAl(user_id):
    payments = fetchAll(user_id)
    if not payments: 
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": payments})


@bp.get("/<payment_id>")
def fetch(payment_id):
    payment = get_payment(payment_id)
    if not payment:
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": payment})


@bp.put("/<payment_id>")
def update(payment_id):
    body = request.get_json()

    payment = update_payment(payment_id, body)
    return jsonify({"data": payment})


@bp.delete("/<payment_id>")
def delete(payment_id):
    delete_payment(payment_id)
    return jsonify({"success": True}), 204