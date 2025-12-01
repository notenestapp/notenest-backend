from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os

NOTE_COL = COLLECTIONS['notes']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")

def create_note(data: dict):
    # if not data.get("users"):
    #     raise ApiError("User id required", 400)
    
    new_doc = database.create_document(
        database_id=DB_ID,
        collection_id=NOTE_COL,
        document_id=ID.unique(),
        data=data
    )
    return new_doc


def fetchAll(user_id: str):
    try:
        notes = database.list_documents(
            database_id=DB_ID,
            collection_id=NOTE_COL,
            queries=[Query.equal("users", user_id)]
        )
        return notes
    except Exception as e:
        return e
    


def get_note(note_id):
    try:
        res = database.get_document(
            database_id=DB_ID,
            collection_id=NOTE_COL,
            document_id=note_id
        )
        return res
    except Exception as e:
        return e


def update_note(note_id: str, data: dict):
    try:
        res = database.update_document(
            database_id=DB_ID,
            collection_id=NOTE_COL,
            document_id=note_id,
            data=data
        )
        return res
    
    except Exception as e:
        return e

def delete_note(note_id: str):
    try:
        database.delete_document(
            database_id=DB_ID,
            collection_id=NOTE_COL,
            document_id=note_id
        )
        return True
    
    except Exception as e:
        return e
    