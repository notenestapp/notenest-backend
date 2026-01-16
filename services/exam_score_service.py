from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os

FEEDBACK_COL = COLLECTIONS['exam_score']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")


def get_user_exam_score(user_id: str):
    try:
        feedbacks = database.list_documents(
            database_id=DB_ID,
            collection_id=FEEDBACK_COL,
            queries=[Query.equal("users", user_id)]
        )
        return feedbacks
    except Exception as e:
        raise e
    

