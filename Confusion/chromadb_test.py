import chromadb
from chromadb.utils import embedding_functions

#Create Chroma client
chroma_client = chromadb.Client()

collection_name = "test"

#Chroma Local embedding functions, not OpenAI embeddings
embedding_funct = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    collection_name, 
    embedding_function=embedding_funct
    )

from chunking import get_document_for_chunking_and_print_chunks
def main():
    documents = get_document_for_chunking_and_print_chunks()

    for doc in documents:
        collection.upsert(ids=doc["chunk_id"], documents=doc["chunk_text"])#This will loop through the documment and adding the chunk to the database

    #This should be the RAG
    query = "Tell me about how to make money"
    results = collection.query(
        query_texts=[query],
        n_results=2
    )
    print(results)#The result here, look at the distances and if the distance is less than 0.85, we will use that without having to scrape
    #If not, we generate google questions and scrape.


if __name__ == "__main__":
    main()
