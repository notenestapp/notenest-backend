
import requests
from groq import Groq
from paddleocr import PaddleOCR
import os


#Try out the mobile model for making it faster and look into those green output and how to fix them
#Work on the forms of pdf, epub, image, word, etc in which input will be sent and then to extract the input
#Do not use paddleocr to read them, basic python can do it. Handle a case where handwritten notes is sent as a pdf.

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
    print("point 1")
    ocr = PaddleOCR(lang='en')

    test_images = ['test image2.jpg', 'test image3.jpg']

    result = ocr.predict(test_images)
    
    for idx, res in enumerate(result):
        #print(f"\n--- Image {idx+1} ---") #Prints out the Image and index number of the image
        combined = " ".join([line[-1][0] for line in res])
        print(f"\n--- Image {idx+1} ---\n{combined}")
        
        #for line in res: #res is the OCR output for that particular image
         #   print(line[-1][0]) #Outputs the actual text from the OCR

    print("point 2")

    print(result)

    """

    texts = result[0]['rec_texts']

    main_text = " ".join(texts)

    print(main_text)

    #final_text = llama3_70b_8192(main_text)
    #print(final_text)

    """
if __name__ == "__main__":
    main()

