from flask import Blueprint, request, jsonify, render_template
from services.payments_service import create_payment, fetchAll, update_payment, delete_payment, get_payment, init_payment, payment_callback, query_payments
from utils.limiter import limiter

bp = Blueprint("payments", __name__, url_prefix="/api/payments")

@bp.post("/create")
@limiter.limit("10 per minute")
def create():
    body = request.get_json()

    # try: 
    #     validated = validate(NoteCreateSchema, body)
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 400
    
    payment = create_payment(body)
    return jsonify({"data": payment}), 201


@bp.get("/")
@limiter.limit("10 per minute")
def get_payments():
    filters = request.args.to_dict()
    print("FILTERS: ", filters)
    data = query_payments(filters)
    return {"data": data}, 200



@bp.post("/initialize")
@limiter.limit("10 per minute")
def initialize_payment():
    try:
        data = request.get_json()

        response = init_payment(data)
        print("Response from the payment init", response)
        return {"data": response}, 200
    except Exception as e:
        print("error in initialization: ", e)


@bp.get("/callback")
@limiter.limit("10 per minute")
def callback():
    try:
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
    except Exception as e:
        print("error in callback call function", e)



@bp.get("/user/<user_id>")
@limiter.limit("10 per minute")
def fetchAl(user_id):
    payments = fetchAll(user_id)
    if not payments: 
        return jsonify({"error": "Not Found"}), 404
    return jsonify({"data": payments})


@bp.get("/<payment_id>")
@limiter.limit("10 per minute")
def fetch(payment_id):
    try:
        payment = get_payment(payment_id)
        if not payment:
            return jsonify({"error": "Not Found"}), 404
        return jsonify({"data": payment})
    except Exception as e:
        print("Error fetching payment: ", e)


@bp.put("/<payment_id>")
@limiter.limit("10 per minute")
def update(payment_id):
    body = request.get_json()
    print("Updating Payment document: ", payment_id, body)

    payment = update_payment(payment_id, body)
    return jsonify({"data": payment})


@bp.delete("/<payment_id>")
@limiter.limit("10 per minute")
def delete(payment_id):
    delete_payment(payment_id)
    return jsonify({"success": True}), 204