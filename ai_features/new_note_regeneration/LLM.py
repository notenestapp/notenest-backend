from groq import Groq
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def gemini(system_prompts, user_prompts):
    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model = "gemini-3-flash-preview",
        contents = user_prompts,#"Teach me about Miller Indices. Step by step while solving problems",
        config=types.GenerateContentConfig(
            system_instruction=system_prompts#"You are a rude teacher and reply in short outputs."
        )
    )
    return response.text

#The llm for classification
def qwen_qwen3_32b(system_prompt, user_prompt):
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {   
                'role': 'system', 
                'content': system_prompt
            },
            {
                'role':'user',
                'content': user_prompt
            }
            ],
        temperature=0.2,
        max_completion_tokens=4096,
        top_p=0.95,
        stream=True,
        stop=None,
        reasoning_effort="default",
    )

    response = ""
    for chunk in completion:
        response += chunk.choices[0].delta.content or ""
    return response

#For now this is only cleaning up the extracted text
def llama_3_1_8b_instant(system_prompt, user_prompt, max_token):
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",# "qwen/qwen3-32b",
        messages=[
            {   
                'role': 'system', 
                'content': system_prompt
            },
            {
                'role':'user',
                'content': user_prompt
            }
            ],
        max_tokens=max_token,
        temperature=0.2,
        max_completion_tokens=1024,
        top_p=0.95,
        stream=True,
        stop=None
    )

    response = ""
    for chunk in completion:
        response += chunk.choices[0].delta.content or ""
    return response

#The LLM for regeneration.
def llama_3_3_70b_versatile2(system_prompt, user_prompt, max_token):
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                'role':'system',
                'content':f"{system_prompt}"
            },
            {
                'role':'user',
                'content':f"{user_prompt}"
            }],
        
        max_tokens=max_token,
        temperature=0.2,
        max_completion_tokens=4096,
        top_p=0.95,
        stream=True,
        stop=None,
    )

    response = "" 
    for chunk in completion:
        response += chunk.choices[0].delta.content or ""
    return response