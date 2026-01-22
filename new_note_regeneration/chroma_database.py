import chromadb
from chromadb.utils import embedding_functions

#Store the extracted text chunks and the reference chunks in the database
def chroma_db(collection_name):
    #Create Chroma client
    #chroma_client = chromadb.Client()
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
#collection = client.create_collection(name="test_collection")

    #Chroma Local embedding functions, not OpenAI embeddings
    embedding_funct = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    collection = chroma_client.get_or_create_collection(
        collection_name, 
        embedding_function=embedding_funct
        )
    return collection
