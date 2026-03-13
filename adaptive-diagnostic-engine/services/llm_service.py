from openai import OpenAI
from app.config import OPENAI_API_KEY
import json


client = OpenAI(api_key=OPENAI_API_KEY)


def generate_study_plan(session: dict) -> list:
    history = session["history"]
    ability = session["ability_score"]

    incorrect = [h for h in history if not h["correct"]]
    weak_topics = list({h["topic"] for h in incorrect})
    difficulties = [h["difficulty"] for h in history]

    summary = {
        "final_ability_score": round(ability, 4),
        "total_questions": session["questions_answered"],
        "total_correct": sum(1 for h in history if h["correct"]),
        "weak_topics": weak_topics,
        "difficulty_progression": [round(d, 2) for d in difficulties],
    }

    prompt = f"""You are an adaptive learning assistant. Based on this test performance, 
generate a 3-step personalized study plan as a JSON array.

Performance Summary:
{json.dumps(summary, indent=2)}

Return ONLY a JSON array with exactly 3 objects, each containing:
- "step" (integer 1-3)
- "topic" (string - the topic to study)
- "recommendation" (string - specific actionable advice)

Focus on the weak topics: {', '.join(weak_topics) if weak_topics else 'General review'}.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
        )
        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception:
        return [
            {"step": 1, "topic": weak_topics[0] if weak_topics else "General", "recommendation": "Review fundamentals of this topic."},
            {"step": 2, "topic": weak_topics[1] if len(weak_topics) > 1 else "Practice", "recommendation": "Solve practice problems at increasing difficulty."},
            {"step": 3, "topic": "Test Strategy", "recommendation": "Take timed practice tests to build endurance."},
        ]
