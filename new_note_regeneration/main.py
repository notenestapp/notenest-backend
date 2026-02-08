import re
import requests
import time
import os
from dotenv import load_dotenv
import LLM

load_dotenv()

#First it will count the overrall page before it extracts and if it exceeds a certain number tell the user to reduce the 
#input or after extracting the text, if it exceeds a token limit, then will send the user out.

def main(notes):

    global_input_limit = 2500
    global_output_limit = 600

    question_generation_input = 400
    question_generation_output_token = 40

    clean_text_input = 800
    clean_text_output = 250

    classification_text_input = 400
    classification_text_output = 50

    retrieval_context_total = 120
    retrieval_max_chunks = 3
    retrieval_chunk_limit = 350

    draft_input = 1200
    draft_output = 500

    final_merge_input = 1500
    final_merge_output = 500

    #STEP 1: Extract Documents
    try:
        text = "" #The extracted text
        ocr_text = False
        for note in notes:
            from text_extraction import ocr, extract_pdf, extract_docx
            if note.endswith(".pdf"):
                print("Extracting from pdf")
                text += extract_pdf(note)
                print("Extracted successfully from the pdf")

            elif note.endswith(".docx"):
                #Docx extraction
                print("\nExtracting from docx")
                text += extract_docx(note)
                print("Extracted successfully from the docx")

            else:#Anything else the OCR will handle it.
                #OCR extraction
                print("\nRunning OCR")
                text += ocr(note)[1]
                ocr_text = True
        
    except Exception as e:
        print(f"Couldn't extract text from images. Error: {e}")
        raise e
    
    #When user inputs the text, we will count the tokens and if it exceed, split it and clean both, then join both
    from text_chunking import count_tokens, chunk_text_by_tokens, enforce_token_budget
    
    model = "llama-3.1-8b-instant"
    token_count = count_tokens(text, model)

    split_ocr_text = []
    if token_count >= global_input_limit:
        split_ocr_text = chunk_text_by_tokens(text, overlap=0)
    else:
        print("Another another testing line")
        pass

    #STEP 2: Clean up the text before chunking it
    clean_text = []
    cleanedup_text = ""
    if len(split_ocr_text) > 0:
        for texts in split_ocr_text:
            split_text = texts["chunk_text"]
            try:
                if ocr_text is True:
                    note_cleanup_system_prompt = "" #Empty. Nothing is being passed in as system prompt

                    from prompts import note_cleanup_user_prompt
                    cleanup_user_prompt = note_cleanup_user_prompt(split_text)

                    from LLM import llama_3_1_8b_instant
                    clean_text += llama_3_1_8b_instant(note_cleanup_system_prompt, cleanup_user_prompt, clean_text_output)
                    cleanedup_text += "".join(clean_text)

            except Exception as e:
                print(f"Couldn't clean up the OCR text: {e}")

    else:
        print("Another of such testing line")
        try:
            if ocr_text is True:
                note_cleanup_system_prompt = "" #Empty. Nothing is being passed in as system prompt

                from prompts import note_cleanup_user_prompt
                cleanup_user_prompt = note_cleanup_user_prompt(text)

                from LLM import llama_3_1_8b_instant
                clean_text += llama_3_1_8b_instant(note_cleanup_system_prompt, cleanup_user_prompt, clean_text_output)
                
                cleanedup_text += "".join(clean_text)

        except Exception as e:
            print(f"The input token is less than require but couldn't clean up the OCR text: {e}")
        pass
    #print(cleanedup_text)

    #STEP 3: Chunking the cleaned extracted text
    try:
        all_chunks = chunk_text_by_tokens(cleanedup_text) #These are the chunks of cleaned text
    except Exception as e:
        print("Coulnt Chunk:", e)

    #STEP 6: CLASSIFICATION THEN CACHE AND REUSE
    try:
        from cache_and_reuse import find_cached_expansion
        name = "NoteNest_Vector_Database"

        from chroma_database import chroma_db
        NoteNest_Vector_Database = chroma_db(name)#The database for knowledge expansion
        chunk_number = 0
        regenerated_note = ""

        youtube_links = [] #The list of youtube links gotten from google CSE
        
        explanation_search_questions = [] #Questions generated for explanation chunks
        other_search_questions = []#Question generated for other chunks
        
        explanation_chunk = [] #The chunks that were labelled as examples
        other_chunk = [] #The chunks that were labelled as examples
     
        explanation_token_count = 0#Assuming that for each loop, it gets the token count and add them up and get the final number we will use in regenerating the chunk
        other_token_count = 0#Assuming that for each loop, it gets the token count and add them up and get the final number we will use in regenerating the chunk

        for chunk in all_chunks:
            chunk_text = chunk["chunk_text"]
            print(f"This is the chunk text: {chunk_text}")
            chunk_token = chunk["token_count"]
            print("This is the chunk token", chunk_token)

            label = ""

            #STEP 3: CLASSIFY EACH CHUNK
            try:
                #if found_knowledge_expansion is False:
                print("----NO INFORMATION COULD BE FOUND IN THE DATABASE SO A SEARCH HAS TO BE RUN.-----\n")

                #from LLM import qwen_qwen3_32b #Import the llm
                from prompts import classification_user_prompt, search_queries_system_prompt, generate_example_question, generate_explanation_question, generate_general_questions#import the prompt
                import prompts #To import the classification system prompt

                #For classification of the chunk
                class_system_prompt = prompts.classification_system_prompt
                class_user_prompt = classification_user_prompt(chunk_text)

                classification = enforce_token_budget(class_system_prompt, class_user_prompt, classification_text_input)
                
                label = llama_3_1_8b_instant(classification[0], classification[1], classification_text_output)#.split("</think>")[1].strip()
                print(label)

                #STEP 4: SEPERATING CHUNKS INTO ONE LIST
                try:
                    search_system_prompt = search_queries_system_prompt()
                    
                    if label == "Explanation":          
                        explanation_token_count = explanation_token_count + chunk_token
                        explanation_chunk.append(chunk_text)

                    #elif label == "Example":
                        #append it to an example list

                    else:
                        other_token_count = other_token_count + chunk_token
                        other_chunk.append(chunk_text)
                    
                except Exception as e:
                    print(f"Error while seperating chunks into the correct classifications: {e}")

            except Exception as e:
                print("Error while classifying the chunk: {e}")
    

        #GENERATE GOOGLE SEARCH QUESTIONS
        all_explanation_chunk = "".join(explanation_chunk)
        all_other_chunk = "".join(other_chunk)

        if len(explanation_chunk) > 0: 
            search_user_prompt = generate_explanation_question(all_explanation_chunk)
            
            generating_questions = enforce_token_budget(search_system_prompt, search_user_prompt, question_generation_input)
            explanation_questions = llama_3_1_8b_instant(generating_questions[0], generating_questions[1], question_generation_output_token)#.split("</think>")[1].strip()
            
            print(f"\n {explanation_questions}\n")

            extracted_explanation_search_questions = re.findall(r'"(.*?)"', explanation_questions)
            print(f"/n -------✅{extracted_explanation_search_questions}")
            explanation_search_questions.extend(extracted_explanation_search_questions)
            print(f"Search questions for explanation chunk: {explanation_search_questions}")
        else:
            pass

        if len(other_chunk) > 0:
            search_user_prompt = generate_general_questions(all_other_chunk)
            other_questions = llama_3_1_8b_instant(search_system_prompt, search_user_prompt, question_generation_output_token)#.split("</think>")[1].strip()
            
            extracted_other_search_questions = re.findall(r'"(.*?)"', other_questions)
            other_search_questions.extend(extracted_other_search_questions)
            print(f"Search questions for other chunk: {other_search_questions}")    
        else:
            pass

        #if the example chunk you'll create is not empty,
            #call the past questions database
        
        
        #FIND EXISTING KNOWLEDGE EXPANSION IN THE DATABASE
        try:
            chunk_number += 1

            cached_expansion = ""
            if len(explanation_search_questions) > 0:
                print(f"\n-----WE ARE WORKING ON CHUNK NUMBER EXPLANATION CHUNK------\n")
                for query in explanation_search_questions:    
                    cached_expansion = find_cached_expansion(query, NoteNest_Vector_Database)
                    print(f"\n-----This is the response in the database {cached_expansion}-----")
            else:
                pass
            
            if len(other_search_questions) > 0:         
                for query in other_search_questions:    
                    cached_expansion = find_cached_expansion(query, NoteNest_Vector_Database)
                    print(cached_expansion)
            else:
                pass

            import prompts
            regen_system_prompt = prompts.regeneration_system_prompt

            #This one works. When result is found, even if it is an empty list, it regenerates the note
            if cached_expansion != "None":
                try:
                    from prompts import regeneration_user_prompt
                    from LLM import llama_3_3_70b_versatile2 
                    #Take the text and pass into an LLM
                    print("\n----USING INFORMATION GOTTEN FROM THE KNOWLEDGE EXPANSION DATABASE----\n")

                    regen_user_prompt = regeneration_user_prompt(chunk_text, cached_expansion)

                    regeneration = enforce_token_budget(regen_system_prompt, regen_user_prompt, draft_input)

                    regenerated_chunk = llama_3_3_70b_versatile2(regeneration[0], regeneration[1], draft_output)
                    print (f"\n-----✅This is the final regenerated content of chunk number explanation chunk----\n{regenerated_chunk}")
                    #regenerated_note += "\n".join(regenerated_chunk)

                    #print(regenerated_note)
                except Exception as e:
                    print(f"Something went wrong while searching for existing content in the knowledge expansion database: {e}")
            else:
                #QUERYING GOOGLE CSE
                CSE_url = "https://www.googleapis.com/customsearch/v1"
                google_search_api_key = os.getenv("google_search_api_key")
                search_engine_id = ["d3098cdee83bc4200", "d19967565d73e4696"]#One id is for google search and the other is for YouTube search
                google_links = [] #The list of links gotten from google CSE
                
                scrapes = 0
                knowledge_expansion = ""
                topic = ""
                clean_explanation_scraped_content = ""
                clean_other_scraped_content = ""

                from search_and_scrape import build_payload, make_requests, scraped_content, clean_scraped_text

                #QUERYING GOOGLE AND SCRAPING THE EXPLANATION CHUNK
                if len(explanation_search_questions) > 0:
                    try:        
                        for query in explanation_search_questions:
                            google_id = search_engine_id[0] 
                            google_payload = build_payload(google_search_api_key, google_id, query)
                            google_response = make_requests(CSE_url, google_payload)
                            google_links.extend(google_response)

                            # Get YouTube link for the same current query
                            youtube_id = search_engine_id[1] 
                            youtube_payload = build_payload(google_search_api_key, youtube_id, query)
                            youtube_response = make_requests(CSE_url, youtube_payload)
                            youtube_links.extend(youtube_response)
                        
                        print(f"The google links for the explanation chunks: {google_links}\n The youtube links for the explanation chunks: {youtube_links}")

                        for link in google_links:
                            url = link.replace("https://", "").replace("http://", "").replace("www.", "")
                            domain =url.split("/")[0]
                            if domain == "youtube.com":
                                pass
                            else:
                                scrapes += 1
                                if scrapes != 2:
                                    print(f"\n------This is the google link for the explanation chunk I want to try scraping {link}-------\n")
                                    knowledge_expansion += scraped_content(link)[0]
                                    topic += scraped_content(link)[1]
                                    time.sleep(5)
                                    clean_explanation_scraped_content += clean_scraped_text(knowledge_expansion)

                        print(f"----This is the clean scraped explanation content {clean_explanation_scraped_content}------")
                        #Here, feed this into the llm and regenerate the final note
                        
                    except Exception as e:
                        print(f"There was an issue querying and scraping the explanation chunk: {e}")
                else:
                    pass
                
                #QUERYING GOOGLE AND SCRAPING THE OTHER CHUNK
                if len(other_search_questions) > 0:
                    try:
                        for query in explanation_search_questions:
                            google_id = search_engine_id[0] 
                            google_payload = build_payload(google_search_api_key, google_id, query)
                            google_response = make_requests(CSE_url, google_payload)
                            google_links.extend(google_response)

                            # Get YouTube link for the same current query
                            youtube_id = search_engine_id[1] 
                            youtube_payload = build_payload(google_search_api_key, youtube_id, query)
                            youtube_response = make_requests(CSE_url, youtube_payload)
                            youtube_links.extend(youtube_response)
                        
                        print(f"The google links for the other chunks: {google_links}\n The youtube links for the other chunks: {youtube_links}")

                        for link in google_links:
                            url = link.replace("https://", "").replace("http://", "").replace("www.", "")
                            domain =url.split("/")[0]
                            if domain == "youtube.com":
                                pass
                            else:
                                scrapes += 1
                                if scrapes != 2:
                                    print(f"\n------This is the google link for the other chunk I want to try scraping {link}-------\n")
                                    knowledge_expansion += scraped_content(link)[0]
                                    topic += scraped_content(link)[1]
                                    time.sleep(5)
                                    clean_other_scraped_content += clean_scraped_text(knowledge_expansion)

                        print(f"------This is the clean scraped other content {clean_other_scraped_content}-----")
                        #Here, feed this into the llm and regenerate the final note

                    except Exception as e:
                        print(f"There was an issue querying and scraping the other chunk: {e}")

                else:
                    pass

        except Exception as e:
            print(f"Something is failing but I have no idea why: {e}")

    except Exception as e:
        print(f"Couldn't get content from the database. Error: {e}")#This is housing a lot morethan the cache and reuse and is needed for the fallback
        #Then continue with the fall back

    if cached_expansion == "None":
        new_knowledge = f"{clean_explanation_scraped_content}\n {clean_other_scraped_content}"
        print(new_knowledge)

        #CHUNKING THE NEW EXTRACTED INFORMATION AND SAVING EACH CHUNK TO THE KNOWLEDGE EXPANSION DATABASE

        from cache_and_reuse import save_expansion 
        try:
            chunk_new_knowledge = chunk_text_by_tokens(new_knowledge) #These are the chunks of text for the scraped content
            for chunking in chunk_new_knowledge:
                chunking_text = chunking["chunk_text"]
                chunking_id = chunking["chunk_id"]
                
                save_the_expansion = save_expansion(chunking_text, chunking_id, topic, NoteNest_Vector_Database)
                print(f"-----Id of the chunk{chunking_id}----\n  -----Result from saving the scraped content to the knowledge expansion database {save_the_expansion}------")
        
        except Exception as e:
            print(f"Couldn't save the new scraped information to the knowledge expansion database. Error: {e}")
    else:
        pass

    #REGENERATING THE note for explanation chunks
    try:      
        if len(explanation_chunk) > 0:
            token = clean_explanation_scraped_content.split()
            trauncate_scrapped_content = " ".join(token[:2000])
            
            regen_user_prompt = prompts.regeneration_user_prompt(all_explanation_chunk, trauncate_scrapped_content)

            regeneration_scrapped_content = enforce_token_budget(regen_system_prompt, regen_user_prompt, draft_input)
            
            regenerate_explanation_chunk = LLM.llama_3_3_70b_versatile2(regeneration_scrapped_content[0], regeneration_scrapped_content[1])
            print(regenerate_explanation_chunk)
            regenerated_note = "".join(regenerate_explanation_chunk)
        else:
            pass

        if len(other_chunk) > 0:
            token = clean_other_scraped_content.split()
            trauncate_scrapped_content = " ".join(token[:2000])
            
            regen_user_prompt = regeneration_user_prompt(all_other_chunk, other_token_count, trauncate_scrapped_content) 
            
            regeneration_scrapped_content = enforce_token_budget(regen_system_prompt, regen_user_prompt, draft_input)
            
            regenerate_other_chunk = LLM.llama_3_3_70b_versatile2(regeneration_scrapped_content[0], regeneration_scrapped_content[1])
            regenerated_note = "".join(regenerate_other_chunk)
        else:
            pass

    except Exception as e:
        print(f"There was an error regeneration the chunks. Error {e}")

    try:
        from prompts import merge_regeneration_user_prompt
        
        merge_half_user_prompt = merge_regeneration_user_prompt(regenerated_note)
        merge_system_prompt = prompts.merge_regeneration_system_prompt
        merge_user_prompt = f"{merge_half_user_prompt}. Here are the YouTube links you should integrate into the right parts of the note:{youtube_links}"
        

        merging = enforce_token_budget(merge_system_prompt, merge_user_prompt, final_merge_input)

        print(f"This is the merging system prompt, I am checking to find the YouTube lnks to be in the note. {merging[0]}\n and this is the user prompt{merging[1]}")
        final_note = LLM.llama_3_3_70b_versatile2(merging[0], merging[1])

        #print(f"-----✅This is the final note{final_note}")

        token = final_note.split()
        trauncate_final_note = " ".join(token[:100])
        #print(f"This is the trauncated note to use and create the topic {trauncate_final_note}")
        topic = LLM.llama_3_3_70b_versatile2(user_prompt=f"This is a regenerated note {trauncate_final_note}, give me an appropriate title for this note based on the topic/subject in studies that is covered in this. Do not explain anything and just give the answer", system_prompt="", max_token=10)

        #print(topic)

    except Exception as e:
        print(f"Failed merging the final note: {e}")

    


if __name__ == "__main__":
    notes = ["test_image2.jpg"]
    main(notes)
    