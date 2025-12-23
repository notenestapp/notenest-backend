from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os
from config.appwrite import account, avatars

USER_COL = COLLECTIONS['users']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")

def get_avatar_url(user_name, size=100):
    # URL encode the name to handle spaces and special characters
    from urllib.parse import quote
    encoded_name = quote(user_name)
    
    # Construct the full URL
    url = f"{os.getenv("APPWRITE_ENDPOINT")}/avatars/initials?name={encoded_name}&width={size}&height={size}"
    
    # Note: Appwrite automatically handles the project ID via the 'X-Appwrite-Project' header
    # or infers it if you are using the client SDK correctly in a client context.
    # For a direct public URL link, the endpoint is sufficient.

    return url

def create_user(data: dict):

    try:
        print(data)
        email = data.get("email")
        accountId = data.get("accountId")
        username = data.get("username")

        avatar = get_avatar_url(user_name=username)

        print(email, account, username, avatar)

        
        new_doc = database.create_document(
            database_id=DB_ID,
            collection_id=USER_COL,
            document_id=accountId,
            data={
                "accountId": accountId,
                "username": username,
                "email": email,
                "avatar": avatar
            }
        )
        print("DOCUMENT", new_doc)
        return {"success": True, "user": new_doc}, 201
    
    except Exception as e:
        print("Error", e)
        raise e



ALLOWED_FILTERS = {
    "username": "username",
    "accountId": "accountId",
    "status": "status",
}

def query_users(filters):
    try: 
        queries = []

        for key, val in filters.items():
            if key not in ALLOWED_FILTERS:
                raise KeyError(f"Filter '{key}' is not allowed")
            appwrite_field = ALLOWED_FILTERS[key]
            queries.append(Query.equal(appwrite_field, val))

        results = database.list_documents(
            database_id=DB_ID,
            collection_id=USER_COL,
            queries=queries
        )

        return results['documents']
    except Exception as e:
        raise e




def get_user(user_id):
    try:
        res = database.get_document(
            database_id=DB_ID,
            collection_id=USER_COL,
            document_id=user_id
        )
        return res
    except Exception as e:
        raise e


def update_user(user_id: str, data: dict):
    try:
        res = database.update_document(
            database_id=DB_ID,
            collection_id=USER_COL,
            document_id=user_id,
            data=data
        )
        return res
    
    except Exception as e:
        raise e

def add_streak(user_id: str):
    try:
        user = get_user(user_id)
        new_streak = user['streak'] + 1
        res = update_user(user_id=user_id, data={"streak": new_streak})
        return {"Success": True}
    
    except Exception as e:
        raise e
    



def reset_streak(user_id: str):
    try:
        res = update_user(user_id=user_id, data={"streak": 1})
        return {"Success": True}
    
    except Exception as e:
        raise e

def delete_user(user_id: str):
    try:
        res = database.delete_document(
            database_id=DB_ID,
            collection_id=USER_COL,
            document_id=user_id
        )
        return True
    
    except Exception as e:
        raise e
    