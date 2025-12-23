from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os

SUBSCRIPTION_COL = COLLECTIONS['subscription']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")

def create_subscription(data: dict):
    
    try:
        new_doc = database.create_document(
            database_id=DB_ID,
            collection_id=SUBSCRIPTION_COL,
            document_id=ID.unique(),
            data=data
        )
        return new_doc
    except Exception as e:
        raise e


def fetchUserSubs(user_id: str):
    try:
        subscriptions = database.list_documents(
            database_id=DB_ID,
            collection_id=SUBSCRIPTION_COL,
            queries=[Query.equal("users", user_id)]
        )
        print("Subs", subscriptions)
        return subscriptions['documents']
    except Exception as e:
        print(e)
        raise e
    


def get_subscription(subscription_id):
    try:
        res = database.get_document(
            database_id=DB_ID,
            collection_id=SUBSCRIPTION_COL,
            document_id=subscription_id
        )
        return res
    except Exception as e:
        raise e


def update_subscription(subscription_id: str, data: dict):
    try:
        res = database.update_document(
            database_id=DB_ID,
            collection_id=SUBSCRIPTION_COL,
            document_id=subscription_id,
            data=data
        )
        return res
    
    except Exception as e:
        raise e

def delete_subscription(subscription_id: str):
    try:
        database.delete_document(
            database_id=DB_ID,
            collection_id=SUBSCRIPTION_COL,
            document_id=subscription_id
        )
        return True
    
    except Exception as e:
        raise e
    