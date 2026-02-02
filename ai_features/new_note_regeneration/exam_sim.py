import re
from ai_features.new_note_regeneration import LLM
from  ai_features.new_note_regeneration import text_chunking
from ai_features.new_note_regeneration import cache_and_reuse
from  ai_features.new_note_regeneration import chroma_database
from  ai_features.new_note_regeneration import prompts
from ai_features.new_note_regeneration.text_extraction import run_ocr
#When we set to multiple choice questions, the questions gotten qre too easy so we have to maybe manually determine of it is multple choice or obj from the psq to gauge the questions to make.

#Run OCR, clean the text, and chunk it
def run_ocr_and_chunk(image):
    system_prompt = ""
    print("\nRunning OCR")

    past_questions = run_ocr(image)[1]#This is the extracted text from the past question

    chunk_past_question = text_chunking.chunk_text_by_tokens(past_questions)
        
    clean_user_prompt = prompts.note_cleanup_user_prompt(past_questions)
    cleanup_pastquestion = LLM.llama_3_1_8b_instant(clean_user_prompt, system_prompt, max_token=500)

    return chunk_past_question, cleanup_pastquestion

def LLM_model(user_prompt, system_prompt, max_tokens=800):
    print("We are running the model")

    try:
        # Always try Gemini first
        return LLM.gemini(user_prompt, system_prompt)

    except Exception as e:
        error_message = str(e)

        # Only fallback for transient / infra failures
        if (
            "503" in error_message or
            "UNAVAILABLE" in error_message or
            "Connection" in error_message
        ):
            print("Gemini failed, falling back to LLAMA")
            return LLM.llama_3_3_70b_versatile2(
                user_prompt,
                system_prompt,
                max_token=max_tokens
            )

        # Anything else is a real failure
        raise

    
def exam_simulation(image, content, no_of_questions, type_of_question, model):
    """
    user_prompt = f
        Create {no_of_questions} practice questions based on this reference style: {text_from_image}
        Use this content as inspiration where relevant: {content}

        FORMAT RULE (MANDATORY):
        Each question must be immediately followed by the options and then its answer.
        Even if the input reference was in a different type, create questions in this type {type_of_question}
        Do NOT create a separate answers section.

        FORMAT EXACTLY LIKE THIS:

        Q1. <question> 
        A1. <answer>

        Q2. <question>
        A2. <answer>

        Repeat until complete.
    """
    user_prompt = f"Create {no_of_questions} practice questions of type {type_of_question} and give their answers"#This will then be when no content and no image
    system_prompt = ""
    topic = ""

    print("Testing, its just taking its sweet time")

    name = "Past_Question_Database"
    Past_Question_Database = chroma_database.chroma_db(name)
    
    if image and content:
        print("All")
        extracted_from_image = run_ocr_and_chunk(image)
        text_from_image = extracted_from_image[1]
        chunked_text_from_image = extracted_from_image[0]
        print("Done extracting images")
        
        #user_prompt = f"Study this style of asking questions {text_from_image} and in the same level of diffculty, style and method, create {no_of_questions} of practice questions and give their answers from a mix of the study questions and this content: {content} "#and give their answers side by side."
        user_prompt = f"""
            Create {no_of_questions} practice questions of type {type_of_question}based on this reference style, level of difficulty and method: {text_from_image}
            Use this content as inspiration where relevant: {content}

            FORMAT RULE (MANDATORY):
            Each question must be immediately followed by the options and then its answer.
            Even if the input reference was in a different type, create questions in this type {type_of_question}
            Do NOT create a separate answers section.

            FORMAT EXACTLY LIKE THIS:

            Q1. <question>
            A. <option>
            B. <option>
            C. <option>
            D. <option>
            A1. <answer>

            Q2. <question>
            A. <option>
            B. <option>
            C. <option>
            D. <option>
            A2. <answer>

            Repeat until complete.
        """

        print("This is the prompt", user_prompt)
        # new_questions = LLM.gemini(user_prompt, system_prompt)

        # topic = LLM.llama_3_3_70b_versatile2(user_prompt=f"This is a practice question that was generated {new_questions}, give me an appropriate title for the practice questions and give their answers, based on the topic/subject in studies that is covered in this. Do not explain anything and just give the answer", system_prompt="", max_token=10)

        for chunk in chunked_text_from_image:
            chunk_text = chunk["chunk_text"]
            chunk_id = chunk["chunk_id"]
            save_the_past_question = cache_and_reuse.save_expansion(chunk_text, chunk_id, topic, Past_Question_Database)

    elif image and not content:
        extracted_from_image = run_ocr_and_chunk(image)
        text_from_image = extracted_from_image[1]
        chunked_text_from_image = extracted_from_image[0]

        print("There is image input but no extra content so getting from database")

        all_the_content_found_in_the_database = []#A list of all the content in the VDB that is similar to the question/chunk of this past question
        user_prompt = ""
        content = ""

        for chunk in chunked_text_from_image:
            chunk_text= chunk["chunk_text"]
            #chunk_id = chunk["chunk_id"]
            
            query_user_prompt = f"Summarise this into a query to run semantic search in a vector database to get the best output. THE TEXT\n{chunk_text}. Do not explain anything and just give the answer"
            query = LLM.llama_3_3_70b_versatile2(query_user_prompt, system_prompt, max_token=100)

            get_past_question_from_database = cache_and_reuse.find_cached_expansion(query, Past_Question_Database)

            if get_past_question_from_database != "None":
                print("Content found in the database")

                #Maybe remove the if else statement and just use a general user prompt that states and acept a content from the db but it would be empty
                all_the_content_found_in_the_database.append(get_past_question_from_database)
                content = " ".join(all_the_content_found_in_the_database)
                
                user_prompt = f"""
                    Create {no_of_questions} practice questions of type {type_of_question} based on this reference style, level of difficulty {text_from_image}
                    These are similar questions gotten from the database:{content} you can repeat these questions if they are relevant and in line with the original or generate new ones based on them.

                    FORMAT RULE (MANDATORY):
                    Each question must be immediately followed by the options and then its answer.
                    Even if the input reference was in a different type, create questions in this type {type_of_question}
                    Do NOT create a separate answers section.

                    FORMAT EXACTLY LIKE THIS:

                    Q1. <question>
                    A. <option>
                    B. <option>
                    C. <option>
                    D. <option>
                    A1. <answer>

                    Q2. <question>
                    A. <option>
                    B. <option>
                    C. <option>
                    D. <option>
                    A2. <answer>

                    Repeat until complete.
                """
            

                #user_prompt = f"Study this style of asking questions {text_from_image} and in the same level of diffculty, style and method, create {no_of_questions} of practice questions from a mix of the study questions. These are similar questions gotten from the database:{content} you can repeat these questions if they are relevant and in line with the original or generate new ones based on them and give their answers."
                #exam_questions = LLM.llama_3_3_70b_versatile2(user_prompt, system_prompt, max_token=500)

            else:
                print("No content found in the database")
                user_prompt = f"""Study this style of asking questions {text_from_image} and in the same level of diffculty,
                    style and method, and create {no_of_questions} practice questions.
                    FORMAT RULE (MANDATORY):
                    Each question must be immediately followed by the options and then its answer.
                    Even if the input reference was in a different type, create questions in this type {type_of_question}
                    Do NOT create a separate answers section.

                    FORMAT EXACTLY LIKE THIS:

                    Q1. <question>
                    A. <option>
                    B. <option>
                    C. <option>
                    D. <option>
                    A1. <answer>

                    Q2. <question>
                    A. <option>
                    B. <option>
                    C. <option>
                    D. <option>
                    A2. <answer>

                    Repeat until complete.
                    """
        
            #Content and no image
    elif not image and content:
        print("Content: ", content)
        user_prompt = f"""
            Create {no_of_questions} practice questions of type {type_of_question} based on the content of this note: {content}

            FORMAT RULE (MANDATORY):
            Each question must be immediately followed by the options and then its answer.
            Even if the input reference was in a different type, create questions in this type {type_of_question}
            Do NOT create a separate answers section.

            FORMAT EXACTLY LIKE THIS:

            Q1. <question>
            A. <option>
            B. <option>
            C. <option>
            D. <option>
            A1. <answer>

            Q2. <question>
            A. <option>
            B. <option>
            C. <option>
            D. <option>
            A2. <answer>

            Repeat until complete.
            If you do not follow the format exactly, the output will be discarded.
        """
        # new_questions = LLM_model(model, user_prompt, system_prompt)
        # #new_questions = LLM.gemini(user_prompt, system_prompt)


        # topic = LLM.llama_3_3_70b_versatile2(user_prompt=f"This is a practice question that was generated {new_questions}, give me an appropriate title for the practice questions based on the topic/subject in studies that is covered in this. Do not explain anything and just give the answer", system_prompt="", max_token=10)

# There was an error that isnt 503 UNAVAILABLE: Connection error.

    print("User prompt: ", user_prompt)
    new_questions = LLM_model(user_prompt, system_prompt)
    print("Done Extracting questions")
    #new_questions = LLM.gemini(user_prompt, system_prompt)


    topic = LLM.llama_3_3_70b_versatile2(user_prompt=f"This is a practice question that was generated {new_questions}, give me an appropriate title for the practice questions based on the topic/subject in studies that is covered in this. Do not explain anything and just give the answer", system_prompt="", max_token=10)
    print("Topic: ", topic)
    # if chunked_text_from_image:
    #     for chunk in chunked_text_from_image:
    #         chunk_text= chunk["chunk_text"]
    #         chunk_id = chunk["chunk_id"]
            
    #         print(f"\n\n\n This is the chunk id: {chunk_id}\n\n")

    #         save_the_past_question = cache_and_reuse.save_expansion(chunk_text, chunk_id, topic, Past_Question_Database)
    #         print(f"Result of saving the expansion: {save_the_past_question}")
    
    #There will be content and no image
    
    #elif not image and not content:
        #For now users will have to either upload a psq or use their note, not none
        #Maybe these guys can input a general topic or something

    # else: 
    #     new_questions = LLM_model(model, user_prompt, system_prompt)
        #new_questions = LLM.gemini(user_prompt, system_prompt)
        #When there is no content and no image, we will need to be maybe a topic or something.

    #print(f"\nThis is the title: {topic}")
    #print("Exam questions----\n", new_questions)
    return topic, new_questions


def parse_questions(text: str):
    questions = {}

    # Split text by question numbers
    blocks = re.split(r"\n(?=Q\d+\.)", text.strip())

    for block in blocks:
        # Match question number and text
        q_match = re.search(r"Q(\d+)\.\s*(.*)", block)
        if not q_match:
            continue

        q_num = q_match.group(1)

        # Skip duplicate questions
        if q_num in questions:
            continue

        # Extract question text (until first option)
        question_text = re.split(r"\nA\.", block, maxsplit=1)[0]
        question_text = question_text.replace(f"Q{q_num}.", "").strip()

        # Extract options
        options = dict(re.findall(r"\n([A-D])\.\s*(.+)", block))

        # Extract answer
        answer_match = re.search(rf"A{q_num}\.\s*([A-D])", block)
        answer = answer_match.group(1) if answer_match else None

        questions[q_num] = {
            f"Q{q_num}": {
                "question": question_text,
                "options": options,
                "answer": answer
            }
        }

    return list(questions.values())


def main(image=None, no_of_questions="10", content=None, type_of_questions='multiple choice'):
    try:
        model = "gemini"
        #use_model = model(model, )
        gemini_model = exam_simulation(image, content, no_of_questions, type_of_questions, model)
        print("I dont get what is happening")
        topic = gemini_model[0]
        new_questions = gemini_model[1]

        print(f"{topic}\n {new_questions}")
        

        #print(f"{topic} \n{new_questions}")
        print(f"{topic} \n {parse_questions(new_questions)}")
        return parse_questions(new_questions)

    except Exception as e: #To test this thing, simulate an error.
        #print(f"This is the error message: {e}")
        error_message = str(e)#The error mesgae you egt
        # if "503" in error_message or "UNAVAILABLE" in error_message:
        #     print("Gemini overloaded and we are switching to LLAMA")
        #     model = "LLAMA"
        #     LLAMA_model = exam_simulation(image, content, no_of_questions, type_of_questions, model)
        #     topic = LLAMA_model[0]
        #     new_questions = LLAMA_model[1]
        #     print(f"{topic} \n{new_questions}")
        #     #return topic, parse_questions(new_questions)
        # else:
        print(f"There was an error that isnt 503 UNAVAILABLE: {e}") #raise e

if __name__ == "__main__":
    image = "exam_sim_test.jpeg"
    #content = "Random knowledge includes surprising facts like octopuses having three hearts, honey never spoiling, Scotland's national animal being the unicorn, and that the shortest war (Anglo-Zanzibar) lasted only 38 minutes, while history reveals Romans used urine as mouthwash and the American flag was designed by a high schooler. Science adds that your brain burns many calories, aurora borealis has its own music, Mount Everest isn't tallest, and lightning is hotter than the sun's surface, while biology shows clownfish are born male and can become female. "
    content = ""
    no_of_questions = "10"
    type_of_question = "multiple choice"
    main(image, content, no_of_questions, type_of_question)