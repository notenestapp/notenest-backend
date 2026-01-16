from config.appwrite import COLLECTIONS, database
import os
import random

PHRASE_COL = COLLECTIONS['catchphrases']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")




def fetchAll():
    try:
        phrases = database.list_documents(
            database_id=DB_ID,
            collection_id=PHRASE_COL,
        )
        return phrases['documents']
    except Exception as e:
        raise e



def getPhrase():
    number = random.randrange(0, 10)
    
    phrases = fetchAll()

    return phrases[number]