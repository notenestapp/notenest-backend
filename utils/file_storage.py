import tempfile
import os
from PIL import Image

MAX_SIZE = (1280, 1280)


def get_file(file_obj):
    try:
        filename = (file_obj.filename or "").lower()
        ext = os.path.splitext(filename)[1]

        if ext not in [".jpg", ".jpeg", ".png", ".bmp", ".pdf", ".webp"]:
            ext = ".jpg"  # force a supported extension

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            file_obj.save(tmp.name)
            temp_path = tmp.name

        if ext in [".jpg", ".jpeg", ".png", ".webp"]:
            with Image.open(temp_path) as img:
                img = img.convert("RGB")
                img.thumbnail(MAX_SIZE)
                img.save(temp_path, format="JPEG", quality=85)

        return temp_path
    except Exception as e:
        raise e
