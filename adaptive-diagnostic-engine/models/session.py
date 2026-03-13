from pydantic import BaseModel, Field
from typing import List, Optional


class HistoryItem(BaseModel):
    question_id: str
    difficulty: float
    correct: bool
    topic: str


class Session(BaseModel):
    session_id: str
    ability_score: float = 0.5
    questions_answered: int = 0
    history: List[HistoryItem] = []
    completed: bool = False


class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str


class StudyPlanStep(BaseModel):
    step: int
    topic: str
    recommendation: str


class TestResult(BaseModel):
    session_id: str
    final_ability_score: float
    total_correct: int
    total_questions: int
    topic_breakdown: dict
    study_plan: List[StudyPlanStep]
