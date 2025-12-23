from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os

COL = COLLECTIONS['read_time']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")


def get_user_read_time(user_id: str):
    try:
        response = database.list_documents(
            database_id=DB_ID,
            collection_id=COL,
            queries=[Query.equal("users", user_id)]
        )
        return response
    except Exception as e:
        raise e
    


def update_user_video_watch_time(data):
    try:
        user_id = data.get("user_id")
        day = data.get("day")
        hours = data.get("hours")

        user_read = get_user_read_time(user_id)

        user_read_document = user_read['documents'][0]
        initial = user_read_document.get(day)
        raw_final = initial + hours
        
        # Round the float off to 4 decimal places for precision in tracking time
        final = round(raw_final, 4) 
        new_data = { day: final}


        response = database.update_document(
            database_id=DB_ID,
            collection_id=COL,
            document_id=user_read_document['$id'],
            data=new_data
        )

        return {"Success": True}
    except Exception as e:
        raise e