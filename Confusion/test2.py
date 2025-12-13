
import requests
from groq import Groq
from paddleocr import PaddleOCR
import os


#Groq APIKEY: Do not send to github
api_key = os.getenv("API_KEY")

#THE LLMs
def llama3_70b_8192(main_text):
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {
                'role':'user',
                'content':f"This text was extracted from an image{main_text}. It is supposed to be a note from class, please make sense of it."
            }],
        temperature=0.6,
        max_completion_tokens=4096,
        top_p=0.95,
        stream=True,
        stop=None,
    )

    response = ''#"" This is a string. It is supposed to be a list. The point is that it will come back with about 5 or more questions to ask. Then the program will be asking google those questions in a loop, one after the other for each index [0], [1], etc
    for chunk in completion:
        response += chunk.choices[0].delta.content or ""#, end=""#this end statement might be a problem. If there errors, check this 

    return response

# good: create once at startup
#ocr = PaddleOCR(lang='en')
from paddleocr import TextRecognition

"""
ocr = PaddleOCR(
    lang='en',
    text_recognition_model_name='en_PP-OCRv4_mobile'
)
"""

model = TextRecognition(model_name="PP-OCRv4_mobile_rec")

def process_image(image_path):
    result = model.predict(image_path)
    return result

def main():
    print("point 1")
    #ocr = PaddleOCR(lang='en')
    #result = ocr.predict('test image2.jpg')

    print("point 2")
    image_path = 'test image2.jpg'

    texts = process_image(image_path)
    note = texts[0]['rec_text']

    #main_text = " ".join(note)

    print(note)

    #final_text = llama3_70b_8192(main_text)
    #print(final_text)


if __name__ == "__main__":
    main()

