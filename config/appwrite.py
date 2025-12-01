import os
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.account import Account
from appwrite.services.storage import Storage
from dotenv import load_dotenv

load_dotenv()


def get_client():

    client = Client()
    (client
        .set_endpoint(os.getenv("APPWRITE_ENDPOINT"))
        .set_project(os.getenv("APPWRITE_PROJECT_ID"))
        .set_key(os.getenv("APPWRITE_API_KEY"))
    )

    return client


client = get_client()
database = Databases(client=client)
account = Account(client=client)
storage = Storage(client=client)

COLLECTIONS = {
    "users": os.getenv("APPWRITE_USERS_COL_ID"),
    "notes": os.getenv('APPWRITE_NOTES_COL_ID'),
    "payments": os.getenv("APPWRITE_PAYMENTS_COL_ID"),
    "chapters": os.getenv("APPWRITE_CHAPTERS_COL_ID"),
    "subscription": os.getenv("APPWRITE_SUBSCRIPTIONS_COL_ID"),
    "feedback": os.getenv("APPWRITE_FEEDBACK_COL_ID"),
    "quotes": os.getenv("APPWRITE_QUOTES_COL_ID"),
    "plans": os.getenv("APPWRITE_PLANS_COL_ID")
}