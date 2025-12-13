
reference_chunks = [
    {"chunk_id": "ref_explanation_1", "chunk_text": "An explanation describes or clarifies how or why something happens, often starting with phrases like 'this means' or 'in simple terms'."},
    {"chunk_id": "ref_explanation_2", "chunk_text": "In simple terms, photosynthesis is the process by which green plants make their food using sunlight."},
    {"chunk_id": "ref_explanation_3", "chunk_text": "Newton's First Law states that an object will remain at rest or in motion unless acted upon by an external force."},

    {"chunk_id": "ref_example_1", "chunk_text": "For example, if you mix red and blue paint, you get purple. This demonstrates color blending."},
    {"chunk_id": "ref_example_2", "chunk_text": "Example: To calculate velocity, divide the distance by the time taken."},
    {"chunk_id": "ref_example_3", "chunk_text": "Let's consider this problem: find the area of a circle with radius 7 cm."},

    {"chunk_id": "ref_formula_1", "chunk_text": "The formula for velocity is v = d / t, where v is velocity, d is distance, and t is time."},
    {"chunk_id": "ref_formula_2", "chunk_text": "Area of a rectangle = length * width."},
    {"chunk_id": "ref_formula_3", "chunk_text": "Ohm's Law is represented as V = IR."},
    {"chunk_id": "ref_formula_4", "chunk_text": "The formula for kinetic energy is KE = 1/2 * m * v^2."},

    {"chunk_id": "ref_reference_1", "chunk_text": "According to a study published in Nature (2019), climate change affects crop yields significantly."},
    {"chunk_id": "ref_reference_2", "chunk_text": "See also: 'The Laws of Thermodynamics', Britannica, 2023 edition."},
    {"chunk_id": "ref_reference_3", "chunk_text": "As stated in Wikipedia, the human brain contains approximately 86 billion neurons."},
    {"chunk_id": "ref_reference_4", "chunk_text": "According to research by Einstein in 1905, light behaves as both a wave and a particle."},
]


import chromadb
from chromadb.utils import embedding_functions


#Create Chroma client
chroma_client = chromadb.Client()

collection_name = "Test_Vector_Database"

#Chroma Local embedding functions, not OpenAI embeddings
embedding_funct = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    collection_name, 
    embedding_function=embedding_funct
    )

#Find a good threshold, then arrange it in the correct code, then move on to handle the llm fallback tomorrow.

def main():
    for ref in reference_chunks:
        collection.upsert(ids=ref["chunk_id"], documents=ref["chunk_text"])
#Also upsert the newchunks with this
    query = "Example: Take a ball at 2m/s with negligible air restance and velocity of 20 in 60 seconds"
    results = collection.query(
        query_texts=[query],
        n_results=2
    )

    print("Query :", query)
    print(results)

    closest_id = results["ids"][0][0]      # "ref_formula_1"
    distance = results["distances"][0][0]  # 0.21

        
    if 0.2 < distance < 0.75:   # confident match
        label = closest_id.split("_")[1]  # "formula"
    else:
        label = "uncertain"

    print(label)


if __name__ == "__main__":
    main()

