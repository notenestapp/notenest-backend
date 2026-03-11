from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os
import json
from services.chapters_service import get_chapter, fetchAllChapters, fetchAllNoteChapters
from ai_features.new_note_regeneration.exam_sim import main
from services.credit_history_service import create_credit_record
from services.user_service import get_user, update_user
from utils.file_storage import get_file

EXAM_COL = COLLECTIONS['exam']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")

def create_exam(data: dict):
    try: 

        questions = []
        urls = []

        # # For each object add the url to the list
        for file_obj in data['files']:
            print("File Object:", file_obj)
            url = get_file(file_obj)
            print("File url: ", url)
            urls.append(url)

        if urls and data['chapter_id'] and data["note_id"]: 
            print("or note, chapter, and images")
            note = get_chapter(chapter_id=data['chapter_id'])
            print("Note: ", note, "for note, chapter, and images")
            content = note['content_string']
            questions = main(
                image=urls[0],
                content=content,
                no_of_questions=data['no_of_questions']
            )

        elif urls and data['note_id'] and not data['chapter_id']:
            print("for note, no chapter, and images")
            notes = fetchAllNoteChapters(data['note_id'])
            print("Note: ", notes, "for note, no chapter, and images")
            content = ''
            for note in notes['documents']: 
                content += note['content_string']

            questions = main(
                image=urls[0],
                content=content,
                no_of_questions=data['no_of_questions']
            )
        
        elif urls and not data['note_id'] and not data['chapter_id']:
            print("For only images")
            questions = main(
                image=urls[0],
                no_of_questions=data['no_of_questions']
            )

        elif data["note_id"] and data['chapter_id'] and not urls:
            print("for note, chapter, and no images")
            note = get_chapter(chapter_id=data['chapter_id'])
            print("Note: ", note, "for note, chapter, and no images")
            content = note['content_string']
            questions = main(
                content=content,
                no_of_questions=data['no_of_questions']
            )

        elif data['note_id'] and not data['chapter_id'] and not urls:
            print("for note, no chapter, and no images")
            print("Note Id: ", data['note_id'])
            nots = fetchAllNoteChapters(data['note_id'])
            notes = nots['documents']
            print("Note: ", notes, "for note, no chapter, and no images")
            content = ''
            for note in notes:
                con = note.get('content_string')

                if con is None:
                    continue  # or con = ""

                content += "\n"
                content += str(con)


            questions = main(
                content=content,
                no_of_questions=data['no_of_questions']
            )
            

   

        new_doc = database.create_document(
            database_id=DB_ID,
            collection_id=EXAM_COL,
            document_id=ID.unique(),
            data={
                "questions": json.dumps(questions),
                "users": data['user_id']
            }
        )
        if (new_doc['questions']):
            # IF EXAM GENERATION IS SUCCESSFUL
            record = create_credit_record({"user_id": data['user_id'], "amount": int(data['cost']), "title": "Exam Generation", "type": "debit",})

            user = get_user(data['user_id'])
            
            if (user["isSubscribed"] == False):
                initial_credit = user['credits']

                final_credit = int(initial_credit) - int(data['cost'])

                update_user(data['user_id'], {
                    "credits": final_credit
                })






        return new_doc
    except Exception as e:
        raise e



def fetchAll(user_id: str):
    try:
        exams = database.list_documents(
            database_id=DB_ID,
            collection_id=EXAM_COL,
            queries=[Query.equal("users", user_id), Query.order_desc("$createdAt")]
        )
        return exams
    except Exception as e:
        raise e
    
def fetch_exam_stats(user_id: str):
    try:
        result = database.list_documents(
            database_id=DB_ID,
            collection_id=EXAM_COL,
            queries=[
                Query.equal("users", user_id),
                Query.order_desc("$createdAt"),
            ],
        )

        documents = result.get("documents", [])

        if not documents:
            return {
                "averageScore": 0,
                "totalTime": 0,
                "lastCreatedAt": None,
                "totalExams": 0,
            }

        total_score = 0
        total_time = 0
        counted_scores = 0

        for doc in documents:
            summary_raw = doc.get("summary")
            if not summary_raw:
                continue

            try:
                summary = json.loads(summary_raw)
            except json.JSONDecodeError:
                continue

            score = summary.get("scorePercentage")
            time = summary.get("time")

            if isinstance(score, (int, float)):
                total_score += score
                counted_scores += 1

            if isinstance(time, (int, float)):
                total_time += time

        average_score = (
            total_score / counted_scores if counted_scores > 0 else 0
        )
        total_time_hours = total_time / 3600

        last_created_at = documents[0].get("$createdAt")

        return {
            "averageScore": round(average_score, 2),
            "totalTime": round(total_time_hours, 2),
            "lastCreatedAt": last_created_at,
            "totalExams": len(documents),
        }

    except Exception as e:
        print("Error fetching exam stats:", e)
        raise
    


def get_exam(exam_id):
    try:
        res = database.get_document(
            database_id=DB_ID,
            collection_id=EXAM_COL,
            document_id=exam_id
        )
        return res
    except Exception as e:
        raise e


def update_exam(exam_id: str, data: dict):
    try:
        res = database.update_document(
            database_id=DB_ID,
            collection_id=EXAM_COL,
            document_id=exam_id,
            data=data
        )
        return res
    
    except Exception as e:
        raise e

def delete_exam(exam_id: str):
    try:
        database.delete_document(
            database_id=DB_ID,
            collection_id=EXAM_COL,
            document_id=exam_id
        )
        return True
    
    except Exception as e:
        raise e
    