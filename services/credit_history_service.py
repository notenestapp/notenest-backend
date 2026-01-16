from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os
from datetime import datetime

# filepath: c:\Users\hp\Desktop\Projects\HACKATHON\flask_test\notenest-backend\services\credit_history.py

CREDIT_HISTORY_COL = COLLECTIONS['credit_history']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")


def create_credit_record(data: dict):
    try:
        user_id = data.get("user_id")
        amount = data.get("amount")
        title = data.get("title"),
        typ = data.get("type")
        
        new_doc = database.create_document(
            database_id=DB_ID,
            collection_id=CREDIT_HISTORY_COL,
            document_id=ID.unique(),
            data={
                "users": user_id,
                "amount": amount,
                "type": typ,
                "title": title,
            }
        )
        print("CREDIT RECORD", new_doc)
        return new_doc, 201
    
    except Exception as e:
        print("Error", e)
        raise e


def get_credit_history(user_id: str):
    try:
        results = database.list_documents(
            database_id=DB_ID,
            collection_id=CREDIT_HISTORY_COL,
            queries=[Query.equal("users", user_id)]
        )
        return results['documents']
    
    except Exception as e:
        raise e


# def get_total_credits(user_id: str):
#     try:
#         records = get_credit_history(user_id)
#         total = sum(record['credits'] for record in records)
#         return total
    
#     except Exception as e:
#         raise e


# def delete_credit_record(record_id: str):
#     try:
#         res = database.delete_document(
#             database_id=DB_ID,
#             collection_id=CREDIT_HISTORY_COL,
#             document_id=record_id
#         )
#         return True
    
#     except Exception as e:
#         raise e