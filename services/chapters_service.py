from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
from typing import TypeVar, List
import os
from ai_features.new_note_regeneration.main import main
from services.push_service import send_push_notification
from services.user_service import get_user
from services.notes_service import get_note, update_note
from utils.text_standardizer import parse_to_sections, extract_dynamic_title
from utils.file_storage import get_file
import json



T = TypeVar('T')

CHAPTER_COL = COLLECTIONS['chapters']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")

def create_chapter(data: dict):
    # if not data.get("users"):
    #     raise ApiError("User id required", 400)
    
    try:
        new_doc = database.create_document(
            database_id=DB_ID,
            collection_id=CHAPTER_COL,
            document_id=ID.unique(),
            data=data
        )

        return new_doc
    except Exception as e:
        print("Error from creating Chapter: ", e)
        raise e

def cut_text(text: str, length: int = 70) -> str:
    # THis function gets the description of the chapter by cutting the regenerated note and returning the first 100 chars
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    if length < 0:
        raise ValueError("length must be non-negative")

    return text[:length]


def generate_chapter(note_id, user_id, fileObj: List[T]):
    try:
        urls = []

        # For each object add the url to the list
        for file_obj in fileObj:
            print("File Object:", file_obj)
            url = get_file(file_obj)
            print("File url: ", url)
            urls.append(url)

        response = None

        # Generate new note from ai

        result = main(urls)
        chapter, title = result
        if not chapter:
            raise ValueError("Failed to generate chapter content")
        chapter = chapter or ""
        # print("Chapters: ", chapter)
        standard_text = parse_to_sections(chapter)
        # # title = extract_dynamic_title(chapter)
        
        # # # FIX: Use json.dumps() to get a string, NOT jsonify()
        content_to_upload = json.dumps(standard_text) 

        # #Fetching the noteData

        note_data = get_note(note_id=note_id)
        number = (note_data.get('last_num') or 0) + 1


        # # # Upload Note to appwrite and get the response body
        response = create_chapter({
            "noteId": note_id,
            "title": title,
            "content": content_to_upload,
            "content_string": chapter,
            "description": cut_text(chapter),
            "file": None
        })
        # print("Response: ", response)

        # #Push Notification
        user = get_user(user_id=user_id)

        send_push_notification(
            user_id=user_id, 
            title=f"Hey, {user['username']}",
            body="Your Note Is Ready",
            data={
                "type": "chapter",
                "chapter_id": response['$id'],
                "user_id": user_id
            }
            )
        update_note(note_id=note_id, data={
            "last_num": number,
        })

        return response

    except Exception as e:
        print("Error regenerating note: ", e)
        raise e



def fetchAll(user_id: str):
    try:
        chapters = database.list_documents(
            database_id=DB_ID,
            collection_id=CHAPTER_COL,
            queries=[
                Query.equal("users", user_id),
                Query.order_desc("$createdAt")
                ]
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

        queries.append(Query.order_desc("$createdAt"))
        

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
    