from datetime import datetime, timedelta

import urllib
from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os
import secrets
import requests
from services.subscriptions_service import create_subscription, fetchUserSubs, update_subscription
from services.user_service import update_user





PAYMENTS_COL = COLLECTIONS['payments']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")

def create_payment(data: dict):
   try:
        new_doc = database.create_document(
            database_id=DB_ID,
            collection_id=PAYMENTS_COL,
            document_id=ID.unique(),
            data=data
        )
        return new_doc
   except Exception as e:
       raise e


def fetchAll(user_id: str):
    try:
        payments = database.list_documents(
            database_id=DB_ID,
            collection_id=PAYMENTS_COL,
            queries=[Query.equal("users", user_id), Query.limit(limit=8), Query.order_desc("$createdAt")]
        )
        print("Payments: ", payments)
        return payments['documents']
    except Exception as e:
        raise e
    

ALLOWED_FILTERS = {
    "amount": "amount",
    "name": "name",
    "users": "users",
    "status": "status",
    "type": "type"
}

def query_payments(filters):
    try:
        queries = []

        for key, val in filters.items():
            if key not in ALLOWED_FILTERS:
                raise KeyError(f"Filter '{key}' is not allowed")
            appwrite_field = ALLOWED_FILTERS[key]
            queries.append(Query.equal(appwrite_field, val))

        results = database.list_documents(
            database_id=DB_ID,
            collection_id=PAYMENTS_COL,
            queries=queries
        )
        print("RESULT", results)

        return results['documents']
    except Exception as e:
        raise e




def get_payment(payment_id):
    try:
        print(payment_id)
        res = database.get_document(
            database_id=DB_ID,
            collection_id=PAYMENTS_COL,
            document_id=payment_id
        )
        return res
    except Exception as e:
        raise e


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
        raise e

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
                'name': payment_title,
                "currency": "NGN",
                "type": payment_type
            }
        )

        reference = secrets.token_hex(16)
        

        params = {"transactionId": transaction['$id'], "paymentType": payment_type, 'payment_title': payment_title, "lasting": lasting, "user_id": user['$id'], 'credits': credits, "user_credits": user['credits']}
        callback_url = f"http://54.198.69.197/api/payments/callback?{urllib.parse.urlencode(params)}"


        payload = { 
            "email" : email,
            "amount": amount,
            "reference": reference,
            "metadata" : metadata,
            "callback_url": callback_url
        }


        headers = {
            "Authorization" : f"Bearer {os.getenv('PAYSTACK_SECRET_KEY')}",
            "Content-Type" : "application/json",
        }

        response = requests.post(
            f"{os.getenv('PAYSTACK_BASE_URL')}/transaction/initialize",
            json=payload,
            headers=headers
        )

        res_data = response.json()

        

        return {
            "status": True,
            "authorization_url": res_data['data']['authorization_url'],
            "reference": reference,
            "transactionId": transaction['$id']
        }
    
    except Exception as e:
        print("An error occurred", e)
        raise e
    



def payment_callback(data: dict):

    # "reference": reference,
    #     "transactionId": transactionId,
    #     "payment_type": payment_type,
    #     "payment_title": payment_title,
    #     "lasting": lasting,
    #     "user_id": user_id,
    #     "credits": credits,
    #     "user_credits": user_credits,
    try:
        reference = data["reference"]
        transactionId =  data["transactionId"]
        payment_type = data["payment_type"]
        payment_title = data["payment_title"]
        lasting = data["lasting"]
        user_id = data["user_id"]
        credits = data['credits']
        user_credits = data['user_credits']

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
            return 'payment_not_found.html'

        # Verify transaction with Paystack
        headers = {"Authorization": f"Bearer {os.getenv("PAYSTACK_SECRET_KEY")}" }
        res = requests.get(f"{os.getenv('PAYSTACK_BASE_URL')}/transaction/verify/{reference}", headers=headers)
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
                    response = fetchUserSubs(user_id=user_id)
                    if not response:
                        response1 = create_subscription(
                            data={
                                "users": user_id,
                                "type": payment_title,
                                "start_date": ahhh.get('startDateISOString'),
                                "end_date": ahhh.get('endDateISOString'),
                                'status': 'active'
                            }
                        )
                    else:
                        response1 = update_subscription(
                            subscription_id=response[0]['$id'],
                            data={
                                "type": payment_title,
                                "start_date": ahhh.get('startDateISOString'),
                                "end_date": ahhh.get('endDateISOString'),
                                'status': 'active'
                            }
                        )
                        

                    response2 = update_user(
                        user_id=user_id,
                        data={
                            "isSubscribed": True
                        }
                    )
                    print("Done 2")

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


                    response2 = update_user(
                        user_id=user_id,
                        data={
                            "credits": total_credits
                        }
                    )

                    print(f"Credits updated: {credits_int} + {user_credits_int} = {total_credits}")
                except Exception as e:
                    print(f"Error updating credits: {e}")

            return "payment_success.html"

        
        result = update_payment(
                payment_id=transactionId, 
                data={
                    "status": "failed"
                })
        return "payment_unsuccess.html"

    except Exception as e:
        print("Error in callback", e)
        raise e
