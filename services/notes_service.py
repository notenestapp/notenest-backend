from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os

NOTE_COL = COLLECTIONS['notes']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")

def create_note(data: dict):
    try:
        print(data)
        url = getNoteThumbnail(data.get("name"))
        data["image"] = url
        new_doc = database.create_document(
            database_id=DB_ID,
            collection_id=NOTE_COL,
            document_id=ID.unique(),
            data=data
        )
        return new_doc
    except Exception as e:
        raise e


def fetchAll(user_id: str):
    try:
        notes = database.list_documents(
            database_id=DB_ID,
            collection_id=NOTE_COL,
            queries=[Query.equal("users", user_id)]
        )
        return notes
    except Exception as e:
        raise e
    


def get_note(note_id):
    try:
        res = database.get_document(
            database_id=DB_ID,
            collection_id=NOTE_COL,
            document_id=note_id
        )
        return res
    except Exception as e:
        raise e


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
        raise e

def delete_note(note_id: str):
    try:
        database.delete_document(
            database_id=DB_ID,
            collection_id=NOTE_COL,
            document_id=note_id
        )
        return True
    
    except Exception as e:
        raise e
    

def getNoteThumbnail(title: str):
    try:
        print(title)
        response = database.list_documents(
            database_id=DB_ID,
            collection_id="course_thumbnails",
            queries=[Query.contains("name", title)]
        )
        # print("Number 1: ", response)
        if response['total'] == 0 :
            response = database.list_documents(
                database_id=DB_ID,
                collection_id="course_thumbnails",
                queries=[Query.search("description", title)]
            )
            print("Number 2: ", response)

            if response["total"] == 0:
                response = database.list_documents(
                    database_id=DB_ID,
                    collection_id="course_thumbnails",
                    queries=[Query.contains("name", "else")]
                )

        print("Response: ", response["documents"][0]["url"])
        return response["documents"][0]["url"]
    except Exception as e:
        print(e)
