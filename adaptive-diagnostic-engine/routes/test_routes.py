from fastapi import APIRouter, HTTPException
from app.database import sessions_collection
from models.session import SubmitAnswerRequest
from services.adaptive_engine import (
    select_next_question,
    update_ability,
    is_test_complete,
)
from services.question_service import get_question_by_id, format_question_response
from services.llm_service import generate_study_plan

router = APIRouter(tags=["Test"])


@router.get("/next-question/{session_id}")
def get_next_question(session_id: str):
    session = sessions_collection.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if session["completed"]:
        raise HTTPException(status_code=400, detail="Test already completed.")

    question = select_next_question(session)
    if not question:
        raise HTTPException(status_code=400, detail="No more questions available.")

    return {
        "session_id": session_id,
        "ability_score": round(session["ability_score"], 4),
        "questions_answered": session["questions_answered"],
        "question": format_question_response(question),
    }


@router.post("/submit-answer")
def submit_answer(payload: SubmitAnswerRequest):
    session = sessions_collection.find_one({"session_id": payload.session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if session["completed"]:
        raise HTTPException(status_code=400, detail="Test already completed.")

    question = get_question_by_id(payload.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    already_answered = any(
        h["question_id"] == payload.question_id for h in session["history"]
    )
    if already_answered:
        raise HTTPException(status_code=400, detail="Question already answered.")

    correct = payload.answer.strip().lower() == question["correct_answer"].strip().lower()
    new_ability = update_ability(
        session["ability_score"], question["difficulty"], correct
    )

    history_entry = {
        "question_id": question["id"],
        "difficulty": question["difficulty"],
        "correct": correct,
        "topic": question["topic"],
    }

    sessions_collection.update_one(
        {"session_id": payload.session_id},
        {
            "$set": {
                "ability_score": new_ability,
                "questions_answered": session["questions_answered"] + 1,
            },
            "$push": {"history": history_entry},
        },
    )

    updated_session = sessions_collection.find_one({"session_id": payload.session_id})
    completed = is_test_complete(updated_session)

    if completed:
        sessions_collection.update_one(
            {"session_id": payload.session_id},
            {"$set": {"completed": True}},
        )

    response = {
        "correct": correct,
        "new_ability_score": round(new_ability, 4),
        "questions_answered": updated_session["questions_answered"],
        "completed": completed,
    }

    if not completed:
        next_q = select_next_question(updated_session)
        response["next_question"] = format_question_response(next_q) if next_q else None
    else:
        response["message"] = "Test completed. Use GET /results/{session_id} to view your results."

    return response


@router.get("/results/{session_id}")
def get_results(session_id: str):
    session = sessions_collection.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if not session["completed"]:
        raise HTTPException(status_code=400, detail="Test is not yet completed.")

    history = session["history"]
    total_correct = sum(1 for h in history if h["correct"])

    topic_stats = {}
    for h in history:
        topic = h["topic"]
        if topic not in topic_stats:
            topic_stats[topic] = {"correct": 0, "total": 0}
        topic_stats[topic]["total"] += 1
        if h["correct"]:
            topic_stats[topic]["correct"] += 1

    study_plan = generate_study_plan(session)

    return {
        "session_id": session_id,
        "final_ability_score": round(session["ability_score"], 4),
        "total_correct": total_correct,
        "total_questions": session["questions_answered"],
        "topic_breakdown": topic_stats,
        "study_plan": study_plan,
    }
