
def save_expansion(clean_scrapped_content, chunk_id, topic, knowledge_expansion_collection):
    metadata = {
        "topic": topic#.lower().strip()
    }
    
    knowledge_expansion_collection.upsert(ids=chunk_id, documents=clean_scrapped_content, metadatas=metadata)#chunk_id here means the id of the chunk. It seems thats the id im using through out

    return "Saved to knowledge expansion database"

#Either we will send the entire chunk into the database as a query or we could find a way to extract the topic from the note and search by that
def find_cached_expansion(query, knowledge_expansion_collection):
    results = knowledge_expansion_collection.query(
                query_texts=[query],
                n_results=2
    )

    if not results["ids"] or len(results["ids"][0]) == 0:
        return "None"

    distances = results["distances"][0][0]

    if distances > 0.45:
        knowledge_expansion = results["documents"][0][0]
        return "None"
    
    elif distances < 0.45:
        knowledge_expansion = results["documents"][0][0]

    else:
        return "None"
    
    return knowledge_expansion#, distances