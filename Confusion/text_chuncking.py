import os
import chromadb
from openai import OpenAI
from chromadb.utils import embedding_functions

openai_api_key = os.getenv("OPEN_API_KEY")

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai_api_key, model_name= "text-embedding-3-small"
)

"""
chroma_client = chromadb.PersistentClient(path= "chroma_persistent_storage")
collection_name = "document_qa_collection"
collection = chroma_client.get_or_create_collection(
    name= collection_name, embedding_function= openai_ef
)
"""
"""
#Chunking the text
def split_text(document, chunk_size=1000, chunk_overlap=20):
    chunks = []
    start = 0
    while start < len(document):
        end = start + chunk_size
        chunks.append(document[start:end])
        start = end - chunk_overlap
    return chunks

"""

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

client = OpenAI(api_key=openai_api_key)
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="NoteNest_notes")

"""
#Generate embeddings
def get_openai_embeddings(chunks):
    response = client.embeddings.create(input=chunks, model="text-embedding-3-small")
    embedding = response.data[0].embedding
    print("=== Generating embeddings ===")
    return embedding

"""

# === Generate embeddings ===
def get_openai_embeddings(text_list):
    if isinstance(text_list, str):
        text_list = [text_list]

    response = client.embeddings.create(
        input=text_list,
        model="text-embedding-3-small"
    )
    embeddings = [item.embedding for item in response.data]
    return embeddings

#Extracting the texts from documents
from document_extraction import extract_pdf, extract_docx
def main():
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

    # Print output
    print("=== Token-based Chunking Results ===\n")
    #print(f"")
    #for record in chunk_records:
    #print(f"Chunk ID: {chunk_records[0]['chunk_id']}")
    #print(f"Token Count: {chunk_records[0]['token_count']}")
    #print(f"Text:\n{chunk_records[0]['chunk_text']}\n")
    #print("="*80)
        
    for doc in chunk_records:
        print(f"=== Generating Embedding for one===")
        doc["embedding"] = get_openai_embeddings(doc["chunk_text"])[0]  # first item

    # === Upsert into ChromaDB ===
    print("=== Inserting all chunks into Chroma ===")
    collection.upsert(
        ids=[doc["id"] for doc in chunk_records],
        documents=[doc["chunk_text"] for doc in chunk_records],
        embeddings=[doc["embedding"] for doc in chunk_records],
        metadatas=[{"user_id": doc["user_id"], "note_id": doc["note_id"]} for doc in chunk_records]
    )


    """
    #Generate embeddings for the document chunks
    for doc in chunk_records:
        print("=== Generating Embedding ===")
        doc["embedding"] = get_openai_embeddings(doc["chunk_text"])

    #Upsert documents with embeddings into Chroma
    for doc in chunk_records:
        print("=== Inserting chunks into db;;; ===")
        collection.upsert(
            ids=[doc["id"]], documents=[doc["chunks"]], embeddings=[doc["embedding"]]
        )
    """
    
    """
    chunked_document = []
    chunks = split_text(document)
    for i in chunks:
        print("\n===Splitting document into chunks===")
        chunked_document.append(i)

        print(chunks[0])
    """

    #for i, chunk in enumerate(chunks):
     #   chunked_document.append(doc)
    #splitted_text = split_text()

if __name__ == "__main__":
    main()
