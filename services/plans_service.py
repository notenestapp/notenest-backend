from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os

PLAN_COL = COLLECTIONS['plans']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")




def fetchAll():
    try:
        plans = database.list_documents(
            database_id=DB_ID,
            collection_id=PLAN_COL,
        )
        return plans
    except Exception as e:
        print("fetchAll error:", e)
    


def get_plan(plan_id):
    try:
        res = database.get_document(
            database_id=DB_ID,
            collection_id=PLAN_COL,
            document_id=plan_id
        )
        return res
    except Exception as e:
        return e


    