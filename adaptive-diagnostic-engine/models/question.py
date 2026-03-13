from pydantic import BaseModel, Field
from typing import List, Optional


class Question(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_answer: str
    difficulty: float = Field(ge=0.1, le=1.0)
    topic: str
    tags: List[str] = []


class QuestionResponse(BaseModel):
    id: str
    question: str
    options: List[str]
    difficulty: float
    topic: str
