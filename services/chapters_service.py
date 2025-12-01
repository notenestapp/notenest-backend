from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os

CHAPTER_COL = COLLECTIONS['chapters']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")

def create_chapter(data: dict):
    # if not data.get("users"):
    #     raise ApiError("User id required", 400)
    
    new_doc = database.create_document(
        database_id=DB_ID,
        collection_id=CHAPTER_COL,
        document_id=ID.unique(),
        data=data
    )
    return new_doc


def fetchAll(user_id: str):
    try:
        chapters = database.list_documents(
            database_id=DB_ID,
            collection_id=CHAPTER_COL,
            queries=[Query.equal("users", user_id)]
        )
        return chapters
    except Exception as e:
        return e
    


ALLOWED_FILTERS = {
    "noteId": "noteId",
    "title": "title",
    "user_id": "user_id",
    "status": "status",
}

def query_chapters(filters):
    queries = []

    for key, val in filters.items():
        if key not in ALLOWED_FILTERS:
            raise KeyError(f"Filter '{key}' is not allowed")
        appwrite_field = ALLOWED_FILTERS[key]
        queries.append(Query.equal(appwrite_field, val))

    results = database.list_documents(
        database_id=DB_ID,
        collection_id=CHAPTER_COL,
        queries=queries
    )
    print("RESULT", results)

    return results['documents']




def get_chapter(chapter_id):
    try:
        res = database.get_document(
            database_id=DB_ID,
            collection_id=CHAPTER_COL,
            document_id=chapter_id
        )
        return res
    except Exception as e:
        return e


def update_chapter(chapter_id: str, data: dict):
    try:
        res = database.update_document(
            database_id=DB_ID,
            collection_id=CHAPTER_COL,
            document_id=chapter_id,
            data=data
        )
        return res
    
    except Exception as e:
        return e


def delete_chapter(chapter_id: str):
    try:
        database.delete_document(
            database_id=DB_ID,
            collection_id=CHAPTER_COL,
            document_id=chapter_id
        )
        return True
    
    except Exception as e:
        return e
    