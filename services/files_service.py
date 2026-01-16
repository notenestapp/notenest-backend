import os
from appwrite.input_file import InputFile
from appwrite.services.storage import Storage
from config.appwrite import client

storage = Storage(client)
BUCKET_ID = os.getenv("APPWRITE_FILES_BUCKET_ID")

def upload_file(file_obj):
    try:
        return storage.create_file(
            bucket_id=BUCKET_ID,
            file_id="unique()",
            file=InputFile.from_bytes(
                file_obj.read(),
                file_obj.filename
            )
        )
    except Exception as e:
        raise e

def delete_file(file_id):
    try:
        return storage.delete_file(
            bucket_id=BUCKET_ID,
            file_id=file_id
        )
    except Exception as e:
        raise e

def get_file_url(file_id):
    try: 
        base = os.getenv("APPWRITE_ENDPOINT")
        project = os.getenv("APPWRITE_PROJECT_ID")
        return f"{base}/storage/buckets/{BUCKET_ID}/files/{file_id}/view?project={project}"
    except Exception as e:
        raise e
