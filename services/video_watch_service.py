from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os

COL = COLLECTIONS['video_watch']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")


def update_user_video_watch_time(data):
    try:
        user_id = data.get("user_id")
        day = data.get("day")
        hours = data.get("hours")

        user_video_document = database.list_documents(
            database_id=DB_ID,
            collection_id=COL,
            queries={Query.equal("users", user_id)}
        )['documents']

        new_data = { day: user_video_document[day] + hours}

        response = database.update_document(
            database_id=DB_ID,
            collection_id=COL,
            document_id=user_video_document['$id'],
            data=new_data
        )

        return {"Success": True}
    except Exception as e:
        raise e

def get_user_video_watch_time(user_id: str):
    try:
        feedbacks = database.list_documents(
            database_id=DB_ID,
            collection_id=COL,
            queries=[Query.equal("users", user_id)]
        )
        return feedbacks
    except Exception as e:
        raise e
    

