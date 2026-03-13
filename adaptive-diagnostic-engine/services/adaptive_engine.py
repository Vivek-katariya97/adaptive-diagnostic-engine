import math
from typing import Optional
from app.database import questions_collection, sessions_collection


def calculate_probability(ability: float, difficulty: float) -> float:
    return 1 / (1 + math.exp(-(ability - difficulty)))


def update_ability(ability: float, difficulty: float, correct: bool) -> float:
    probability = calculate_probability(ability, difficulty)
    return ability + 0.3 * (int(correct) - probability)


def select_next_question(session: dict) -> Optional[dict]:
    answered_ids = [h["question_id"] for h in session["history"]]
    ability = session["ability_score"]

    all_questions = list(questions_collection.find({"id": {"$nin": answered_ids}}))
    if not all_questions:
        return None

    return min(all_questions, key=lambda q: abs(q["difficulty"] - ability))


def is_test_complete(session: dict) -> bool:
    return session["questions_answered"] >= 10
