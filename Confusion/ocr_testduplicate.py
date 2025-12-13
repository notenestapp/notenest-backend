
import requests
from groq import Groq
from paddleocr import PaddleOCR
import os

#Search on youtube for a video on reading the text from a pdf
#Might not look into the model thing again for now or continue more research on phone

#Try out the mobile model for making it faster and look into those green output and how to fix them
#Work on the forms of pdf, epub, image, word docx, mobi,.txt etc in which input will be sent and then to extract the input
#Do not use paddleocr to read them, basic python can do it. Handle a case where handwritten notes is sent as a pdf.
#If a file name ends with pdf, send it here, png, send it elsewhere, etc


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

def main():
    print("point 1")#Debugging

    #OCR
    ocr = PaddleOCR(lang='en')
    test_images = ['Confusion/test image2.jpg']#The images
    result = ocr.predict(test_images)#The OCR is processing the images

    print("point 2")#Debugging

    for idx, res in enumerate(result):#The OCR returns json output so we are checking for the rec_texts key which is where the output of the OCR is.
        texts = res["rec_texts"]
        combined = " ".join(texts)
    
    print(f"\n--- Image {idx + 1} ---\n{combined}")
    final_text = llama3_70b_8192(combined)
    print(final_text)

if __name__ == "__main__":
    main()

