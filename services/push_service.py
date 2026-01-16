from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os
import requests
from services.user_service import get_user

TOKEN_COL = COLLECTIONS['push_tokens']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")
EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"




def create_token(user_id, token, platform, is_active):
    try: 
        user = get_user(user_id=user_id)

        # send_push_notification(
        #     user_id=user_id, 
        #     title=f"Welcome, {user['username']}",
        #     body="I hope you have a good time using NoteNest today"
        #     )
        
        #Check if document exists
        existing_document = database.list_documents(
            database_id=DB_ID,
            collection_id=TOKEN_COL,
            queries=[Query.equal("user_id", user_id),]
        )

        existing = existing_document['documents']
        if len(existing) > 0:
            new_doc = database.update_document(
                database_id=DB_ID,
                collection_id=TOKEN_COL,
                document_id=existing[0]['$id'],
                data={
                    "token": token,
                    "platform": platform,
                    "is_active": is_active
                }
            )
        else:
            new_doc = database.create_document(
                database_id=DB_ID,
                collection_id=TOKEN_COL,
                document_id=ID.unique(),
                data={
                    'user_id': user_id,
                    "token": token,
                    "platform": platform,
                    "is_active": is_active
                }
            )
        return new_doc
    except Exception as e:
        raise e




def send_push_notification(user_id, title, body, data=None):
    """
    Send push notifications to all active tokens for a user.

    Args:
        user_id (int): ID of the user
        title (str): Notification title
        body (str): Notification body
        data (dict, optional): Extra payload data
    """

    tokens_documents = database.list_documents(
                database_id=DB_ID,
                collection_id=TOKEN_COL,
                queries=[
                    Query.equal("user_id", user_id),
                    Query.equal("is_active", True)
                    ]
            )
    tokens = tokens_documents['documents']
    if not tokens:
        return {"status": "no_tokens", "message": "No active push tokens found for user"}

    messages = []
    for token_obj in tokens:
        messages.append({
            "to": token_obj['token'],
            "sound": "default",
            "title": title,
            "body": body,
            "data": data or {}
        })

    # Send notifications in batches (Expo recommends <= 100 messages per request)
    batch_size = 100
    responses = []
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i + batch_size]
        try:
            r = requests.post(EXPO_PUSH_URL, json=batch, timeout=10)
            r.raise_for_status()
            result = r.json()
            responses.append(result)
            handle_expo_responses(batch, result)
        except Exception as e:
            print(f"Error sending push notifications: {e}")
            raise e

    return {"status": "ok", "responses": responses}



def handle_expo_responses(messages, results):
    """
    Handles Expo responses, deactivates invalid tokens.
    """
    for message, result in zip(messages, results.get("data", [])):
        status = result.get("status")
        if status == "error":
            code = result.get("details", {}).get("error")
            token_str = message["to"]
            if code in ("DeviceNotRegistered", "MessageRateExceeded", "InvalidCredentials"):
                # deactivate token
                tokens_documents = database.list_documents(
                    database_id=DB_ID,
                    collection_id=TOKEN_COL,
                    queries=[
                        Query.equal("tokens", token_str),
                        Query.equal("is_active", True)
                        ]
                        )
                token_obj = tokens_documents['documents'][0]
                if token_obj:
                    res = database.update_document(
                    database_id=DB_ID,
                    collection_id=TOKEN_COL,
                    document_id=token_obj['$id'],
                    data={
                        "is_active": False
                    }
                )
                    print(f"Deactivated token {token_str} due to {code}")





# def fetchAll(user_id: str):
#     try:
#         feedbacks = database.list_documents(
#             database_id=DB_ID,
#             collection_id=FEEDBACK_COL,
#             queries=[Query.equal("users", user_id)]
#         )
#         return feedbacks
#     except Exception as e:
#         raise e
    


# def get_feedback(feedback_id):
#     try:
#         res = database.get_document(
#             database_id=DB_ID,
#             collection_id=FEEDBACK_COL,
#             document_id=feedback_id
#         )
#         return res
#     except Exception as e:
#         raise e


# def update_feedback(feedback_id: str, data: dict):
#     try:
#         res = database.update_document(
#             database_id=DB_ID,
#             collection_id=FEEDBACK_COL,
#             document_id=feedback_id,
#             data=data
#         )
#         return res
    
#     except Exception as e:
#         raise e

# def delete_feedback(feedback_id: str):
#     try:
#         database.delete_document(
#             database_id=DB_ID,
#             collection_id=FEEDBACK_COL,
#             document_id=feedback_id
#         )
#         return True
    
#     except Exception as e:
#         raise e
    