import tempfile
import os
from PIL import Image

MAX_SIZE = (1280, 1280)


def get_file(file_obj):
    try:
        filename = file_obj.filename.lower()

        # Save to temp file so your existing logic still works
        suffix = os.path.splitext(filename)[1] or ".tmp"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            file_obj.save(tmp.name)
            temp_path = tmp.name

        # Image preprocessing
        if suffix in [".jpg", ".jpeg", ".png", ".webp"]:
            with Image.open(temp_path) as img:
                img = img.convert("RGB")
                img.thumbnail(MAX_SIZE)
                img.save(temp_path, format="JPEG", quality=85)

        return temp_path
    except Exception as e:
        raise e
