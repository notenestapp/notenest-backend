import re
import requests
import time

def main(notes):
    #try:

    #STEP 1: Extract Documents
    
    try:
        text = "" #The extracted text
        for note in notes:
            from text_exctraction import ocr, extract_pdf, extract_docx
            if note.endswith(".pdf"):
                print("Extracting from pdf")
                text = extract_pdf(note)
                print(text)
                print("Text extracted successfully")

            elif note.endswith(".docx"):
                #Docx extraction
                print("\nExtracting from docx")
                text = extract_docx(note)
                print(text)

            else:#Anything else the OCR will handle it.
                #OCR extraction
                print("\nRunning OCR")
                text = ocr(note)[1]
                #print(text)
        
    except Exception as e:
        print(f"Couldn't extract text from images. Error: {e}")

    #Clean up the text before chunking it
    note_cleanup_system_prompt = "You cleanup notes" #Empty. Nothing is being passed in as system prompt

    from prompts import note_cleanup_user_prompt, regeneration_user_prompt
    cleanup_user_prompt = note_cleanup_user_prompt(text)

    from LLM import llama_3_1_8b_instant, llama_3_3_70b_versatile2
    cleanedup_text = llama_3_1_8b_instant(note_cleanup_system_prompt, cleanup_user_prompt)

    #print(f"---This is the cleaned up text of what was extracted : {cleanedup_text}----")

    #STEP 2: Chunking the extracted text
    from text_chunking import chunk_text_by_tokens
    all_chunks = chunk_text_by_tokens(cleanedup_text) #These are the chunks of text


    """
    #Creating the database
    #I dont think this reference and notenest database is necessary because the notenest database is not being queried and we're already using llm for classification which invalidates the reference database
    chunk_name = "NoteNest_Vector_Database"

    chunk_collection = chroma_db(chunk_name)#This is the main NoteNest database

    #Insert extracted text chunks into its own database 
    for chunk in all_chunks:
        chunk_collection.upsert(ids=chunk["chunk_id"], documents=chunk["chunk_text"])#This will loop through all_chunk and adding the chunk to the database
    """

    from prompts import reference_chunks#importing reference chunks list from prompts.py
    from chroma_database import chroma_db
    ref_name = "Reference_Database"
    ref_collection = chroma_db(ref_name) #This is the reference database for classification of the chunks

    #Insert reference chunks into its own database
    for ref in reference_chunks:
        ref_collection.upsert(ids=ref["chunk_id"], documents=ref["chunk_text"])



    #STEP 6: CACHE AND REUSE
    #try:
    from cache_and_reuse import save_expansion, find_cached_expansion
    name = "Knowledge_Expansion_Database"
    knowledge_expansion_collection = chroma_db(name)#The database for knowledge expansion
    chunk_number = 0
    regenerated_note = ""
    youtube_links = [] #The list of youtube links gotten from google CSE


    for chunk in all_chunks:
        chunk_text = chunk["chunk_text"]
        chunk_number += 1
        print(f"\n-----WE ARE WORKING ON CHUNK NUMBER {chunk_number}------\n")
        cached_expansion = find_cached_expansion(chunk_text, knowledge_expansion_collection)#chunk_text is the query into the database
        #print(cached_expansion)
        chunk_token_count = chunk["token_count"]

        #This one works. When result is found, even if it is an empty list, it regenerates the note
        if cached_expansion != "None":
            #Take the text and pass into an LLM
            print("\n----GETTING INFORMATION FROM THE KNOWLEDGE EXPANSION DATABASE----\n")
            import prompts
            regen_system_prompt = prompts.regeneration_system_prompt
            regen_user_prompt = regeneration_user_prompt(chunk_text, chunk_token_count, cached_expansion)
            
            regenerated_chunk = llama_3_3_70b_versatile2(regen_system_prompt, regen_user_prompt)
            print (f"\n-----✅This is the final regenerated content of chunk number {chunk_number}✅----\n{regenerated_chunk}")
            regenerated_note += "\n".join(regenerated_chunk)

        else:
            #STEP 3: Classify each chunk as Explanation, Example, Formular or Reference
            #This should be the RAG. This takes the chunk and classifies it by checking the embedding distance with the reference embeddings
            #print(cached_expansion)
            print("----NO INFORMATION COULD BE FOUND IN THE DATABASE SO A SEARCH HAS TO BE RUN.-----")
            label = ""
            try:
                # Access the value for the specific key 'age'
                #print(f"This is the dictionary value {chunk_text}")#Debugging
                results = ref_collection.query(
                    query_texts=[chunk_text],
                    n_results=2
                )
                
                #print(results)

                closest_id = results["ids"][0][0]      # "ref_formula_1"
                distance = results["distances"][0][0]  # 0.21
                                
                if 0.2 < distance < 0.75:   # confident match
                    label = closest_id.split("_")[1]  # "formula"
                    
                elif distance > 0.75:
                    label = "uncertain"
                    print(label)

                    from LLM import qwen_qwen3_32b #Import the llm
                    from prompts import classification_user_prompt, search_queries_system_prompt, generate_example_question, generate_explanation_question, generate_general_questions#import the prompt
                    import prompts #To import the classification system prompt

                    #For classification of the chunk
                    class_system_prompt = prompts.classification_system_prompt
                    class_user_prompt = classification_user_prompt(chunk_text)
                    #print("\n------THIS ISNT WORKING!!!-----\n")
                    label = qwen_qwen3_32b(class_system_prompt, class_user_prompt).split("</think>")[1].strip()
                    print(label)
                    
                else:
                    label = "uncertain"
                
            except Exception as e:
                print(f"Couldn't classify the chunk. Error: {e}")

            #STEP 4: Generate search queries according to the classification.
            try:
                search_questions = ""
                search_system_prompt = search_queries_system_prompt(label)
                if label == "Explanation":
                    search_user_prompt = generate_explanation_question(chunk_text)
                    search_questions = qwen_qwen3_32b(search_system_prompt, search_user_prompt).split("</think>")[1].strip()
                    #print(search_questions)

                #elif label == "Example":
                    #search_user_prompt = generate_example_question(chunk_text)
                    #search_questions = qwen_qwen3_32b(search_system_prompt, search_user_prompt).split("</think>")[1].strip()
                    #print(search_questions)

                else:
                    search_user_prompt = generate_general_questions(chunk_text)
                    search_questions = qwen_qwen3_32b(search_system_prompt, search_user_prompt).split("</think>")[1].strip()
                    #print(search_questions)

                all_search_questions = []
                all_search_questions = re.findall(r'"(.*?)"', search_questions)
                #print(f"\n-----These are the search questions{all_search_questions}-------")

            except Exception as e:
                print(f"Couldnt generate search queries. Error: {e}")


            #STEP 5: KNOWLEDGE EXPANSION
            try:
                CSE_url = "https://www.googleapis.com/customsearch/v1"
                google_search_api_key = "AIzaSyD42uygkZbP1epbWKj9p--yvKCDTJt-FrM"
                search_engine_id = ["d3098cdee83bc4200", "d19967565d73e4696"]#One id is for google search and the other is for YouTube search
                google_links = [] #The list of links gotten from google CSE
                
                runs = 0
                
                from search_and_scrape import build_payload, make_requests, scraped_content, clean_scraped_text, categorize_link
                for query in all_search_questions:
                    for id in search_engine_id:
                        payload = build_payload(google_search_api_key, id, query)
                        response = make_requests(CSE_url, payload)
                        #print(response)
                        runs += 1
                        if runs != 2:
                            google_links.extend(response)
                        else:
                            payload = build_payload(google_search_api_key, id, query, num= no_of_youtube_videos)
                            youtube_links.extend(response)

                scrapes = 0
                knowledge_expansion = ""
                reddit_url = ""
                topic = ""

                for link in google_links:
                    url = link.replace("https://", "").replace("http://", "").replace("www.", "")
                    domain = url.split("/")[0]
                    if domain == "reddit.com":
                        reddit_url += "".join([link, ".json"]) #from here you have to work on parsing the json    
                        headers = {"User-Agent": "Mozilla/5.0"}  # Reddit requires this to scrap
                        response = requests.get(reddit_url, headers=headers)
                        data = response.json()
                        #print(data) #To continue on how to scrape reddit, from here parse the json
                        #post = data[0]["data"]["children"][0]["data"] These dont work, we'll look at it later on
                        #knowledge_expansion += post["title"]
                        #knowledge_expansion  += post["selftext"]
                        #knowledge_expansion += data[1]["data"]["children"]
                        #knowledge_expansion += scraped_content(reddit_url)#This isnt working. You still cannot scrape reddit

                    #print(knowledge_expansion)

                    primary_sites = categorize_link(domain, link)[0]#The final list of primary google links to scrape for information
                    secondary_sites = categorize_link(domain, link)[1]#The final list of secondary google links to scrape for human touch
                    
                #print("The link category", primary_sites, secondary_sites)

                for url in primary_sites:
                    scrapes += 1
                    if scrapes != 2:
                        knowledge_expansion += scraped_content(url)[0]
                        time.sleep(5)
                        clean_scrapped_content = clean_scraped_text(knowledge_expansion)
                        #Will save the information to the database then truncate it and send to the llm
                        topic += scraped_content(url)[1]

                #print(f"-----This is the scraped content {clean_scrapped_content} ----")

            except Exception as e:
                print(f"Something went wrong while running knowledge expansion and trying to scrape content. Error: {e}")
                from prompts import fallback_user_prompt
                fall_back_user_prompt = fallback_user_prompt(chunk_text, chunk_token_count)
            
                regenerated_chunk = llama_3_3_70b_versatile2(regen_system_prompt, fall_back_user_prompt)
                #print (f"-----✅This is the final regenerated content of chunk number {chunk_number}✅----\n{regenerated_chunk}")
                regenerated_note += "\n".join(regenerated_chunk)



            try:
                from cache_and_reuse import save_expansion
                name = "Knowledge_Expansion_Database"
                knowledge_expansion_collection = chroma_db(name)#The database for knowledge expansion
                
                chunk_id = chunk["chunk_id"] 
                save_the_expansion = save_expansion(clean_scrapped_content, chunk_id, topic, knowledge_expansion_collection)
                print(f"----Id of the chunk{chunk_id}----\n -----Result from saving the expansion: {save_the_expansion}------")

                regen_system_prompt = prompts.regeneration_system_prompt
                token = clean_scrapped_content.split()
                trauncate_scrapped_content = " ".join(token[:2000])

                regen_user_prompt = regeneration_user_prompt(chunk_text, chunk_token_count, trauncate_scrapped_content)
            
                regenerated_chunk = llama_3_3_70b_versatile2(regen_system_prompt, regen_user_prompt)
                #print (f"-----✅This is the final regenerated content of chunk number {chunk_number}✅----\n{regenerated_chunk}")
                regenerated_note += "\n".join(regenerated_chunk)

                #print(f"-----Result from save the expansion: {save_the_expansion}------")

                #Finally, join all the chunks
                no_of_youtube_videos = 2#This will later be calculated from implicit personalisation. To know how many youtube links to be put inside

            except Exception as e:
                print(f"-----Something went wrong while trying to cache knowledge expansion. Error: {e}-----")

    from prompts import merge_regeneration_user_prompt
    merge_user_prompt = merge_regeneration_user_prompt(regenerated_note, youtube_links)
    final_note = llama_3_3_70b_versatile2(regen_system_prompt, merge_user_prompt)

    print(final_note) 




    #except Exception as e:
        #print(f"Something went wrong while trying to cache knowledge expansion. Error: {e}")


    #There should be a fallback where if you there is an error any where, the LLM should regenerate the note itself without context. 
    #Write this in the except blocks for scraping, finding cached, etc.

if __name__ == "__main__":
    notes = "Backend_2/test image2.jpg"
    main(notes)
