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
        raise e

   
    
ALLOWED_FILTERS = {
    "type": "type",
}

def query_plans(filters):
    try: 
        queries = []
        print("Hello")

        for key, val in filters.items():
            if key not in ALLOWED_FILTERS:
                raise KeyError(f"Filter '{key}' is not allowed")
            appwrite_field = ALLOWED_FILTERS[key]
            queries.append(Query.equal(appwrite_field, val))

        results = database.list_documents(
            database_id=DB_ID,
            collection_id=PLAN_COL,
            queries=queries
        )
        print("Documents", results)
        return results
    except Exception as e:
        raise e


def get_plan(plan_id):
    try:
        res = database.get_document(
            database_id=DB_ID,
            collection_id=PLAN_COL,
            document_id=plan_id
        )
        return res
    except Exception as e:
        raise e


    