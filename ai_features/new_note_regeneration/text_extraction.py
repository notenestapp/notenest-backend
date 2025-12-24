import requests
from groq import Groq
from paddleocr import PaddleOCR
import fitz
from docx.api import Document
import os


#The OCR
def ocr(notes):
    # Initialize variables with default values
    idx = 0
    combined = ""
    ocr = PaddleOCR(lang='en', use_angle_cls=True, det_model_dir=None, rec_model_dir=None)

    result = ocr.predict(notes)#The OCR is processing the images
    
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

