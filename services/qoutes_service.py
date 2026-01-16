from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os

QUOTES_COL = COLLECTIONS['quotes']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")

def create_quote(data: dict):
   try: 
        new_doc = database.create_document(
            database_id=DB_ID,
            collection_id=QUOTES_COL,
            document_id=ID.unique(),
            data=data
        )
        return new_doc
   except Exception as e:
       raise e


ALLOWED_FILTERS = {
    "chapters": "chapters",
    "title": "title",
    "user_id": "user_id",
    "status": "status",
}

def query_quotes(filters):
    try: 
        queries = []

        for key, val in filters.items():
            if key not in ALLOWED_FILTERS:
                raise KeyError(f"Filter '{key}' is not allowed")
            appwrite_field = ALLOWED_FILTERS[key]
            queries.append(Query.equal(appwrite_field, val))

        results = database.list_documents(
            database_id=DB_ID,
            collection_id=QUOTES_COL,
            queries=queries
        )

        return results['documents']
    except Exception as e:
        raise e




def fetchAll(user_id: str):
    try:
        quotes = database.list_documents(
            database_id=DB_ID,
            collection_id=QUOTES_COL,
            queries=[Query.equal("users", user_id)]
        )
        return quotes
    except Exception as e:
        raise e
    

#Just in case.
def get_quote(quote_id):
    try:
        res = database.get_document(
            database_id=DB_ID,
            collection_id=QUOTES_COL,
            document_id=quote_id
        )
        return res
    except Exception as e:
        raise e


def update_quote(quote_id: str, data: dict):
    try:
        res = database.update_document(
            database_id=DB_ID,
            collection_id=QUOTES_COL,
            document_id=quote_id,
            data=data
        )
        return res
    
    except Exception as e:
        raise e


def delete_quote(quote_id: str):
    try:
        database.delete_document(
            database_id=DB_ID,
            collection_id=QUOTES_COL,
            document_id=quote_id
        )
        return True
    
    except Exception as e:
        raise e
    