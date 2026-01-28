import tiktoken
import uuid

#Chunking of the text
def chunk_text_by_tokens(text, tokenizer_name="cl100k_base", max_tokens=250, overlap=50):
    enc = tiktoken.get_encoding(tokenizer_name)
    tokens = enc.encode(str(text))
    chunks = []
    start = 0

    while start < len(tokens):
        end = start + max_tokens
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        chunk_id = str(uuid.uuid4())
        chunks.append({
            "chunk_id": chunk_id,
            "chunk_text": chunk_text,
            "token_count": len(chunk_tokens)
        })
        start += max_tokens - overlap  # move forward with overlap

    return chunks

"""
The output is a list of dictionaries in this format
[
    {
        "user_id": "user_123",
        "note_id": "note_789",
        "chunk_id": "...",
        "chunk_text": "...",
        "token_count": 123
    },
    {
        "user_id": "user_123",
        "note_id": "note_789",
        "chunk_id": "...",
        "chunk_text": "...",
        "token_count": 98
    }
]
"""

#To count how many tokens a text is according to the model that is going to be used by the LLM

def count_tokens(string: str, model_name: str) -> int: # -> indicates the return type should be integer and the str indicates the input type should be string
    # Get the appropriate encoding for the model
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Fallback to a default encoding if the model name is not found
        encoding = tiktoken.get_encoding("cl100k_base")
    
    # Encode the string into a list of token integers and return the length
    num_tokens = len(encoding.encode(string))
    return num_tokens


def enforce_token_budget(system_prompt, user_prompt, max_input_tokens, model="llama-3.1-8b-instant"):
    system_tokens = count_tokens(system_prompt, model)
    user_tokens = count_tokens(user_prompt, model)

    if system_tokens >= max_input_tokens:
        raise ValueError("System prompt alone exceeds token budget")

    available_for_user = max_input_tokens - system_tokens

    if user_tokens > available_for_user:
        words = user_prompt.split()
        truncated = []
        running = 0
        for w in words:
            running += count_tokens(w + " ", model)
            if running > available_for_user:
                break
            truncated.append(w)
        user_prompt = " ".join(truncated)

    return system_prompt, user_prompt