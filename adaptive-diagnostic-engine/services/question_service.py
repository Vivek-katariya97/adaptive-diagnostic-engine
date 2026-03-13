from typing import Optional
from app.database import questions_collection


def get_question_by_id(question_id: str) -> Optional[dict]:
    return questions_collection.find_one({"id": question_id})


def get_all_questions() -> list:
    return list(questions_collection.find({}, {"_id": 0}))


def format_question_response(question: dict) -> dict:
    return {
        "id": question["id"],
        "question": question["question"],
        "options": question["options"],
        "difficulty": question["difficulty"],
        "topic": question["topic"],
    }
