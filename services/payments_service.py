from datetime import datetime, timedelta
from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os
import secrets
import requests
from services.subscriptions_service import create_subscription
from services.user_service import update_user




PAYMENTS_COL = COLLECTIONS['payments']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")

def create_payment(data: dict):
    # if not data.get("users"):
    #     raise ApiError("User id required", 400)
    
    new_doc = database.create_document(
        database_id=DB_ID,
        collection_id=PAYMENTS_COL,
        document_id=ID.unique(),
        data=data
    )
    return new_doc


def fetchAll(user_id: str):
    try:
        payments = database.list_documents(
            database_id=DB_ID,
            collection_id=PAYMENTS_COL,
            queries=[Query.equal("users", user_id)]
        )
        return payments
    except Exception as e:
        return e
    


def get_payment(payment_id):
    try:
        res = database.get_document(
            database_id=DB_ID,
            collection_id=PAYMENTS_COL,
            document_id=payment_id
        )
        return res
    except Exception as e:
        return e


def update_payment(payment_id: str, data: dict):
    try:
        res = database.update_document(
            database_id=DB_ID,
            collection_id=PAYMENTS_COL,
            document_id=payment_id,
            data=data
        )
        return res
    
    except Exception as e:
        return e

def delete_payment(payment_id: str):
    try:
        database.delete_document(
            database_id=DB_ID,
            collection_id=PAYMENTS_COL,
            document_id=payment_id
        )
        return True
    
    except Exception as e:
        return e
    
def get_start_and_end(lasting: int):
    # 1. Get the current date/time
    start = datetime.utcnow()
    start_date_iso = start.isoformat() + "Z"  # UTC ISO format

    # 2. Calculate the end date by adding 'lasting' days
    end = start + timedelta(days=lasting)
    end_date_iso = end.isoformat() + "Z"  # UTC ISO format

    return {
        "startDateISOString": start_date_iso,
        "endDateISOString": end_date_iso
    }



def init_payment(data: dict):
    try:
        email = data.get("email")
        amount = data.get("amount")
        user = data.get("user")
        metadata = data.get("metadata", {})
        payment_type = data.get("payment_type")
        payment_title = data.get("title")
        lasting = data.get("lasting")
        credits = data.get('credits')
        print("Payment for: ", user['username'], "Amount: ", amount, "Payment Type: ", payment_type)

        # transaction = database.create_document(
        #     database_id=appwriteConfig['databaseId'],
        #     collection_id=appwriteConfig['paymentCollectionId'],
        #     document_id=ID.unique(),
        #     data={
        #         "users": user['$id'],
        #         "amount": amount//100,
        #     }
        # )

        transaction = create_payment(
            data={
                "users": user['$id'],
                "amount": amount//100,
            }
        )

        reference = secrets.token_hex(16)
        

        params = {"transactionId": transaction['$id'], "paymentType": payment_type, 'payment_title': payment_title, "lasting": lasting, "user_id": user['$id'], 'credits': credits, "user_credits": user['credits']}
        callback_url = f"https://8f6761964ba5.ngrok-free.app/payment/callback?{urllib.parse.urlencode(params)}"


        payload = { 
            "email" : email,
            "amount": amount,
            "reference": reference,
            "metadata" : metadata,
            "callback_url": callback_url
        }


        headers = {
            "Authorization" : f"Bearer {os.getenv("PAYSTACK_SECRET_KEY")}",
            "Content-Type" : "application/json",
        }

        response = requests.post(
            f"{os.getenv("PAYSTACK_SECRET_KEY")}/transaction/initialize",
            json=payload,
            headers=headers
        )

        res_data = response.json()
        print(res_data['data']['authorization_url'])

        

        return {
            "status": True,
            "authorization_url": res_data['data']['authorization_url'],
            "reference": reference,
            "transactionId": transaction['$id']
        }
    
    except Exception as e:
        print(e)
        return { "status": False, "error": str(e)}
    



def payment_callback(data: dict):

    # "reference": reference,
    #     "transactionId": transactionId,
    #     "payment_type": payment_type,
    #     "payment_title": payment_title,
    #     "lasting": lasting,
    #     "user_id": user_id,
    #     "credits": credits,
    #     "user_credits": user_credits,
    
    reference = data["reference"]
    transactionId =  data["transactionId"]
    payment_type = data["payment_type"]
    payment_title = data["payment_title"]
    lasting = data["lasting"]
    user_id = data["user_id"]
    credits = data['credits']
    user_credits = data['user_credits']

    print("Callback: Reference: ", reference, " Transaction ID ", transactionId, "Payment Type: ", payment_title)
    if not reference or not transactionId:
        result = update_payment(transactionId, data={
            "status": "failed"
        })
        # result = database.update_document(
        #     database_id=appwriteConfig['databaseId'],
        #     collection_id=appwriteConfig["paymentCollectionId"],
        #     document_id=transactionId,
        #     data={
        #         "status": "failed"
        #     }
        # )
        return """
        <html>
<head>
    <title>Payment Failed</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            margin: 0;
            padding: 0;
            background: #f8d7da;
            color: #721c24;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
        }

        .container {
            width: 100%;
            padding: 40px 20px;
            text-align: center;
        }

        .icon-circle {
            width: 90px;
            height: 90px;
            background-color: #721c24;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 40px auto 25px auto;
            color: white;
            font-size: 48px;
            font-weight: bold;
        }

        h1 {
            font-size: 1.9rem;
            margin: 10px 0;
            font-weight: 600;
        }

        p {
            font-size: 1rem;
            opacity: 0.85;
            margin-bottom: 35px;
            line-height: 1.5;
            padding: 0 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon-circle">×</div>
        <h1>Payment Failed</h1>
        <p>No reference provided or payment was unsuccessful.</p>
    </div>
</body>
</html>

        """

    # Verify transaction with Paystack
    headers = {"Authorization": f"Bearer {os.getenv("PAYSTACK_SECRET_KEY")}" }
    res = requests.get(f"{os.getenv("PAYSTACK_BASE_URL")}/transaction/verify/{reference}", headers=headers)
    result = res.json()

    if result["data"]["status"] == "success":

        result = update_payment(
            payment_id=transactionId, 
            data={
                "status": "successful"
            })
        # result = database.update_document(
        #     database_id=appwriteConfig['databaseId'],
        #     collection_id=appwriteConfig["paymentCollectionId"],
        #     document_id=transactionId,
        #     data={
        #         "status": "successful"
        #     }
        # )


        if payment_type == "subscription":
            try:
                ahhh = get_start_and_end(lasting=int(lasting))
                print("Ahhhh: ", ahhh)

                response = create_subscription(
                    data={
                        "type": payment_title,
                        "start_date": ahhh.get('startDateISOString'),
                        "end_date": ahhh.get('endDateISOString')
                    }
                )
                # response = database.create_document(
                #     database_id=appwriteConfig['databaseId'],
                #     collection_id=appwriteConfig["subscriptionCollection"],
                #     document_id=ID.unique(),
                #     data={
                #         "type": payment_title,
                #         "start_date": ahhh.get('startDateISOString'),
                #         "end_date": ahhh.get('endDateISOString')

                #     }
                # )

                # response2 = database.update_document(
                #     database_id=appwriteConfig["databaseId"],
                #     collection_id=appwriteConfig['userTableId'],
                #     document_id=user_id,
                #     data={
                #         "isSubscribed": True
                #     }
                # )

                response2 = update_user(
                    user_id=user_id,
                    data={
                        "isSubscribed": True
                    }
                )

            except Exception as e:
                print(f"Error updating subscriptions: {e}")
        elif payment_type == "one-time":
            try:
                # Convert to int, handle string "None" and actual None
                credits_val = credits if credits and credits != "None" else 0
                user_credits_val = user_credits if user_credits and user_credits != "None" else 0
                
                credits_int = int(credits_val)
                user_credits_int = int(user_credits_val)
                total_credits = credits_int + user_credits_int
                
                # response = database.update_document(
                #     database_id=appwriteConfig["databaseId"],
                #     collection_id=appwriteConfig['userTableId'],
                #     document_id=user_id,
                #     data={
                #         "credits": total_credits
                #     }
                # )

                response2 = update_user(
                    user_id=user_id,
                    data={
                        "credits": total_credits
                    }
                )

                print(f"Credits updated: {credits_int} + {user_credits_int} = {total_credits}")
            except Exception as e:
                print(f"Error updating credits: {e}")

        return """
        <html>
<head>
    <title>Payment Successful</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            margin: 0;
            padding: 0;
            background: #ffffff;
            color: #333;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
        }

        .container {
            width: 100%;
            padding: 30px 20px;
            text-align: center;
        }

        .icon-circle {
            width: 90px;
            height: 90px;
            background-color: #4c711c;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 40px auto 25px auto;
            color: white;
            font-size: 48px;
            font-weight: bold;
        }

        h1 {
            font-size: 1.8rem;
            margin: 10px 0 8px 0;
            color: #4c711c;
            font-weight: 600;
        }

        p {
            font-size: 1rem;
            color: #666;
            margin-bottom: 40px;
            padding: 0 10px;
            line-height: 1.5;
        }

        button {
            width: 100%;
            padding: 15px;
            font-size: 1.05rem;
            border: none;
            border-radius: 10px;
            color: white;
            background-color: #2c6ea3;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15);
            transition: opacity 0.3s;
        }

        button:active {
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon-circle">&#10004;</div>
        <h1>Payment Successful</h1>
        <p>Your transaction has been completed successfully.</p>
        <button onclick="window.close()">Continue</button>
    </div>
</body>
</html>

        """

    # Payment failed
    # result = database.update_document(
    #         database_id=appwriteConfig['databaseId'],
    #         collection_id=appwriteConfig["paymentCollectionId"],
    #         document_id=transactionId,
    #         data={
    #             "status": "failed"
    #         }
    #     )
    
    result = update_payment(
            payment_id=transactionId, 
            data={
                "status": "failed"
            })
    return """
    <html>
<head>
    <title>Payment Failed</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            margin: 0;
            padding: 0;
            background: #f8d7da;
            color: #721c24;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
        }

        .container {
            width: 100%;
            padding: 40px 20px;
            text-align: center;
        }

        .icon-circle {
            width: 90px;
            height: 90px;
            background-color: #721c24;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 40px auto 25px auto;
            color: white;
            font-size: 48px;
            font-weight: bold;
        }

        h1 {
            font-size: 1.9rem;
            margin: 10px 0 10px 0;
            font-weight: 600;
        }

        p {
            font-size: 1rem;
            color: #721c24;
            opacity: 0.85;
            margin-bottom: 35px;
            padding: 0 10px;
            line-height: 1.5;
        }

        button {
            width: 100%;
            padding: 15px;
            font-size: 1.05rem;
            border: none;
            border-radius: 10px;
            color: white;
            background-color: #721c24;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15);
            transition: opacity 0.3s;
        }

        button:active {
            opacity: 0.85;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon-circle">×</div>
        <h1>Payment Failed</h1>
        <p>Your transaction could not be completed. Please try again.</p>
        <button onclick="window.close()">Try Again</button>
    </div>
</body>
</html>

    """


