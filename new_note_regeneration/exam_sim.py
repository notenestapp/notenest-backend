
#from LLM import llama_3_3_70b_versatile2, llama_3_1_8b_instant

import LLM
def run_ocr():
    system_prompt = ""
    print("\nRunning OCR")
    from text_extraction import ocr
    past_questions = ocr(image)[1]

    import prompts
    clean_user_prompt = prompts.note_cleanup_user_prompt(past_questions)
    cleanup_pastquestion = LLM.llama_3_1_8b_instant(clean_user_prompt, system_prompt, max_token=500)

    return cleanup_pastquestion
    

def main(image, content, type_of_question, no_of_questions):
    user_prompt = f"Create {no_of_questions} of practice questions from this content: {content}"
    system_prompt = ""

    try:
        if image and content:
            past_question = run_ocr(image)

            print("The extracted past questions\n----", past_question)

            user_prompt = f"Study this style of asking questions {past_question} and create {no_of_questions} of {type_of_question} practice questions from a mix of the study questions and this content: {content}"
            exam_questions = LLM.llama_3_3_70b_versatile2(user_prompt, system_prompt, max_token=200)

        elif image and not content:
            past_question = run_ocr(image)
            #run web scraping

        elif not image and not content:
            #For now users will have to either upload a psq or use their note, not none


        else:
            exam_questions = LLM.llama_3_3_70b_versatile2(user_prompt, system_prompt, max_token=200)


        print("Exam questions----\n", exam_questions)

    except Exception as e:
        print(f"Something went wrong while generating questions: {e}")
    #When a user opens that featue, they select, upload past question, generate from notes or generate from both, from the nternet is the final way.
    #Now, if a user sends to upload from a past question, input will be an image where we will run OCR and say that from these notes as content, create possible questions to answer.
    #So we always have 3 inputs and check if the image is none or if it exists, if not, will use just the note. We can generate the questions from the llm and use regex to break it down into a list where Dean iterates from.
    #You once said that the llm shouldnt be handling the structure and that I should regex or something else to do that.


if __name__ == "__main__":
    image = "exam_sim_test.jpeg"
    content = "Random knowledge includes surprising facts like octopuses having three hearts, honey never spoiling, Scotland's national animal being the unicorn, and that the shortest war (Anglo-Zanzibar) lasted only 38 minutes, while history reveals Romans used urine as mouthwash and the American flag was designed by a high schooler. Science adds that your brain burns many calories, aurora borealis has its own music, Mount Everest isn't tallest, and lightning is hotter than the sun's surface, while biology shows clownfish are born male and can become female. "
    no_of_questions = "10"
    type_of_question = "theory"
    main(image, content, type_of_question, no_of_questions)