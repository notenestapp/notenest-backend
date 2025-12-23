from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os

FEEDBACK_COL = COLLECTIONS['feedback']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")

def create_feedback(data: dict):
    try: 
        new_doc = database.create_document(
            database_id=DB_ID,
            collection_id=FEEDBACK_COL,
            document_id=ID.unique(),
            data=data
        )
        return new_doc
    except Exception as e:
        raise e



def fetchAll(user_id: str):
    try:
        feedbacks = database.list_documents(
            database_id=DB_ID,
            collection_id=FEEDBACK_COL,
            queries=[Query.equal("users", user_id)]
        )
        return feedbacks
    except Exception as e:
        raise e
    


def get_feedback(feedback_id):
    try:
        res = database.get_document(
            database_id=DB_ID,
            collection_id=FEEDBACK_COL,
            document_id=feedback_id
        )
        return res
    except Exception as e:
        raise e


def update_feedback(feedback_id: str, data: dict):
    try:
        res = database.update_document(
            database_id=DB_ID,
            collection_id=FEEDBACK_COL,
            document_id=feedback_id,
            data=data
        )
        return res
    
    except Exception as e:
        raise e

def delete_feedback(feedback_id: str):
    try:
        database.delete_document(
            database_id=DB_ID,
            collection_id=FEEDBACK_COL,
            document_id=feedback_id
        )
        return True
    
    except Exception as e:
        raise e
    