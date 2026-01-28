from config.appwrite import database, COLLECTIONS
from appwrite.id import ID
from appwrite.query import Query
import os
import json
from services.chapters_service import get_chapter, fetchAll
from ai_features.new_note_regeneration.exam_sim import main
from utils.file_storage import get_file

EXAM_COL = COLLECTIONS['exam']
DB_ID = os.getenv("APPWRITE_DATABASE_ID")

def create_exam(data: dict):
    try: 
#         # Call exam function here
        # questions = [{
        #     'Q1': {'question': 'Miller indices are primarily used to describe which of the following in a crystal lattice?', 'options': {'A': 'The position of a single atom', 'B': 'The orientation of a plane within a space lattice', 'C': 'The velocity of an electron through the crystal', 'D': 'The total weight of the unit cell'}, 'answer': 'B'}}, 
        #     {'Q2': {'question': 'What is the first step in the procedure for finding the Miller indices of a plane?', 'options': {'A': 'Take the reciprocal of the intercepts', 'B': 'Enclose the indices in parentheses', 'C': 'Find the intercepts of the plane along the axes (x, y, z)', 'D': 'Reduce the numbers to the smallest integers'}, 'answer': 'C'}}, 
        #     {'Q3': {'question': 'If a plane is parallel to an axis and never intersects it, the intercept is considered to be at infinity (∞). What is the corresponding Miller index for that axis?', 'options': {'A': '1', 'B': '∞', 'C': '0', 'D': '-1'}, 'answer': 'C'}}, 
        #     {'Q4': {'question': 'Which of the following formulas is used to calculate the distance (d) between adjacent parallel planes of indices (h, k, l) for a cubic lattice?', 'options': {'A': 'd = a / (h + k + l)', 'B': 'd = a / (√(h² + k² + l²))', 'C': 'd = a · (√(h² + k² + l²))', 'D': 'd = √(h² + k² + l²) / a'}, 'answer': 'B'}}, 
        #     {'Q5': {'question': 'A plane has intercepts at 1a, 1b, and 1c. What are the Miller indices for this plane?', 'options': {'A': '(1 1 1)', 'B': '(0 0 0)', 'C': '(∞ ∞ ∞)', 'D': '(1 0 0)'}, 'answer': 'A'}}]
        
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
            notes = fetchAll(user_id=data['user_id'])
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
            notes = fetchAll(user_id=data['user_id'])
            print("Note: ", note, "for note, no chapter, and no images")
            content = ''
            for note in notes['documents']: 
                content += note['content_string']

            questions = main(
                content=content,
                no_of_questions=data['no_of_questions']
            )
            

        print("Done", questions, "now, saving to the database")

        new_doc = database.create_document(
            database_id=DB_ID,
            collection_id=EXAM_COL,
            document_id=ID.unique(),
            data={
                "questions": json.dumps(questions),
                "users": data['user_id']
            }
        )
        print("New Doc", new_doc)


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
    