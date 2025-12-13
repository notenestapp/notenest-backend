import requests
from groq import Groq
from paddleocr import PaddleOCR
import fitz
from docx.api import Document
import os

#Try out the mobile model for making it faster and look into those green output and how to fix them
#If a file name ends with pdf, send it here, png, send it elsewhere, etc

#Groq APIKEY: Do not send to github
api_key = os.getenv("API_KEY")

#The OCR
def ocr(notes):#content is the images to me extracted and will later be put in the main file
    ocr = PaddleOCR(lang='en')
    result = ocr.predict(notes)#The OCR is processing the images
    
    for idx, res in enumerate(result):#The OCR returns json output so we are checking for the rec_texts key which is where the output of the OCR is.
        texts = res["rec_texts"]
        combined = " ".join(texts)#To join all the texts found in "rec_texts"

    #output = f"\n--- Image {idx + 1} ---\n{combined}"
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

