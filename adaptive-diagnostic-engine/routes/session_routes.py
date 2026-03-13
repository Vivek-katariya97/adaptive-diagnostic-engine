import uuid
from fastapi import APIRouter, HTTPException
from app.database import sessions_collection
from services.adaptive_engine import select_next_question, is_test_complete
from services.question_service import format_question_response

router = APIRouter(prefix="/session", tags=["Session"])


@router.post("/start")
def start_session():
    session_id = str(uuid.uuid4())

    session = {
        "session_id": session_id,
        "ability_score": 0.5,
        "questions_answered": 0,
        "history": [],
        "completed": False,
    }

    sessions_collection.insert_one(session)

    first_question = select_next_question(session)
    if not first_question:
        raise HTTPException(status_code=500, detail="No questions available. Run the seed script first.")

    return {
        "session_id": session_id,
        "ability_score": 0.5,
        "question": format_question_response(first_question),
    }
