import tempfile
import os

def get_file(file_obj):
    try:
        filename = file_obj.filename.lower()

        # Save to temp file so your existing logic still works
        suffix = os.path.splitext(filename)[1] or ".tmp"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            file_obj.save(tmp.name)
            temp_path = tmp.name

        return temp_path
    except Exception as e:
        raise e
