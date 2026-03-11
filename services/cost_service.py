from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os


def get_costt(data):
    try:
        cost = 0
        if data['type'] == "exam":
            cost = get_exam_cost(data['questionsNumber'], data['noteId'], data['chapterId'], data['imageLength'])

        elif data['type'] == 'note':
            cost = get_note_cost(data['imageLength'], data['documentLength'])
        
        return cost
    except Exception as e:
        print("Error: ", e)
        return e



def get_exam_cost(questionNumber, noteId=None, chapterId=None, imageLength=0):

    base_cost = 10

    # question scaling
    question_cost = int((questionNumber / 5) * 5)

    # image generation cost
    image_cost = imageLength * 3

    # scope cost
    if chapterId:
        scope_cost = 5
    elif noteId:
        scope_cost = 10
    else:
        scope_cost = 0

    total_cost = base_cost + question_cost + image_cost + scope_cost

    return total_cost
    


    

def get_note_cost(imageLength=0, documentLength=0):

    base_cost = 5

    image_cost = imageLength * 4
    document_cost = documentLength * 2

    total_cost = base_cost + image_cost + document_cost

    return total_cost
   
    

