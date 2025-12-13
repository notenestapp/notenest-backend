import tiktoken
import uuid

def chunk_text_by_tokens(text, tokenizer_name="cl100k_base", max_tokens=512, overlap=50):
    enc = tiktoken.get_encoding(tokenizer_name)
    tokens = enc.encode(text)
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


#Extracting the texts from documents
from document_extraction import extract_pdf, extract_docx
def get_document_for_chunking_and_print_chunks():#main():
    document = []
    path = "the-psychology-of-money-9780857197689-9780857197696_compress - Copy.pdf"
    path_docx = "Test-docx.docx"

    get_pdf_content=extract_pdf(path)
    document.append(get_pdf_content)
    get_docx_content= extract_docx(path_docx)
    document.append(get_docx_content)

    print(f"Loaded{len(document)} documents")
    #print(document)

    note = "".join(document)
    user_id = "user_123"
    note_id = "note_789"

    chunks = chunk_text_by_tokens(note, max_tokens=512, overlap=50)

    chunk_records = []
    for chunk in chunks:
        chunk_records.append({
            "user_id": user_id,
            "note_id": note_id,
            "chunk_id": chunk["chunk_id"],
            "chunk_text": chunk["chunk_text"],
            "token_count": chunk["token_count"]
        })

    return chunk_records
"""
    # Print output
    print("=== Token-based Chunking Results ===\n")
    #print(f"")
    #for record in chunk_records:
    print(f"Chunk ID: {chunk_records[0]['chunk_id']}")
    print(f"Token Count: {chunk_records[0]['token_count']}")
    print(f"Text:\n{chunk_records[0]['chunk_text']}\n")
    print("="*80)
        

if __name__ == "__main__":
    main()
"""
