from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os

USER_COL = COLLECTIONS['users']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")

def create_user(data: dict):
    
    new_doc = database.create_document(
        database_id=DB_ID,
        collection_id=USER_COL,
        document_id=ID.unique(),
        data=data
    )
    return new_doc



def get_user(user_id):
    try:
        res = database.get_document(
            database_id=DB_ID,
            collection_id=USER_COL,
            document_id=user_id
        )
        return res
    except Exception as e:
        return e


def update_user(user_id: str, data: dict):
    try:
        res = database.list_documents(
            database_id=DB_ID,
            collection_id=USER_COL,
            document_id=user_id,
            data=data
        )
        return res
    
    except Exception as e:
        return e

def delete_user(user_id: str):
    try:
        res = database.delete_document(
            database_id=DB_ID,
            collection_id=USER_COL,
            document_id=user_id
        )
        return True
    
    except Exception as e:
        return e
    