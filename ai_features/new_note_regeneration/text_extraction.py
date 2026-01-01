import requests
from groq import Groq
from paddleocr import PaddleOCR
import fitz
from docx.api import Document
import os

_ocr_instance = None

def get_ocr():
    global _ocr_instance
    if _ocr_instance is None:
        from paddleocr import PaddleOCR # lazy import
        _ocr_instance = PaddleOCR(
            lang='en',
            use_angle_cls=False, # TURN THIS OFF
            )
    return _ocr_instance
#The OCR


#The OCR
def run_ocr(image_path):
    # Initialize variables with default values
    ocr = get_ocr()
    result = ocr.predict(image_path)
    idx = 0
    combined = ""
    #ocr = PaddleOCR(lang='en', use_angle_cls=True, det_model_dir=None, rec_model_dir=None)

    #result = ocr.predict(notes)#The OCR is processing the images
    
    for idx, res in enumerate(result):#The OCR returns json output so we are checking for the rec_texts key which is where the output of the OCR is.
        texts = res["rec_texts"]
        combined = " ".join(texts)#To join all the texts found in "rec_texts"

    return idx, combined

#Extracting pdfs
def extract_pdf(path):
    doc = fitz.open(path)
    text = "".join([page.get_text() for page in doc])
    return text

#Extracting word documents
def extract_docx(path_docx):
    document = Document(path_docx)
    all_texts = ""
    for p in document.paragraphs:
        all_texts += p.text
        all_texts += "\n"
    return all_texts

