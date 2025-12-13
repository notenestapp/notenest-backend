from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
from typing import TypeVar, List
import os
from ai_features.note_generation.main import main

from services.files_service import get_file_url, upload_file

T = TypeVar('T')

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

def cut_text(text: str, length: int = 100) -> str:
    # THis function gets the description of the chapter by cutting the regenerated note and returning the first 100 chars
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    if length < 0:
        raise ValueError("length must be non-negative")

    return text[:length]


def generate_chapter(note_id, fileObj: List[T]):
    try:
        urls = []

        # For each object, upload the file and add the url to the list
        for obj in fileObj:
            saved = upload_file(obj)
            url = get_file_url(saved["$id"])
            image_urls += url

        # Generate new note from ai
        chapter = main(urls)

        #Upload Note to appwrite and get the response body
        response = create_chapter({
            "noteId": note_id,
            "title": chapter['title'],
            "content": chapter["content"],
            "description": cut_text(chapter['content']),
            "file": urls
        })

        # Return response to route function
        return response

    except Exception as e:
        raise e



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
    try:
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

        return results['documents']
    
    except Exception as e:
        raise e
        




def get_chapter(chapter_id):
    try:
        res = database.get_document(
            database_id=DB_ID,
            collection_id=CHAPTER_COL,
            document_id=chapter_id
        )
        return res
    except Exception as e:
        raise e


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
        raise e


def delete_chapter(chapter_id: str):
    try:
        database.delete_document(
            database_id=DB_ID,
            collection_id=CHAPTER_COL,
            document_id=chapter_id
        )
        return True
    
    except Exception as e:
        raise e
    