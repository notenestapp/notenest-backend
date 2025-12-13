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


def main():
    random_text = "If you want, I can give you: ✅ The function for saving this schema✅ The function for checking if topic exists✅ The function for retrieving cached expansions✅ The function for deciding whether to run the Knowledge Expansion LayerJust tell me:Give me the functions for this."

    chunk = chunk_text_by_tokens(random_text)
    print(chunk)

if __name__ == "__main__":
    main()
