# AI-Driven Adaptive Diagnostic Engine

A production-style backend for 1-Dimensional Adaptive Testing, built with FastAPI, MongoDB, and OpenAI. The engine dynamically selects questions based on a test-taker's evolving ability score using Item Response Theory (IRT), and generates personalized AI-powered study plans upon test completion.

## Features

- Adaptive question selection using simplified IRT
- Real-time ability score tracking
- Session-based test management
- AI-generated personalized study plans via OpenAI
- RESTful API with automatic Swagger documentation

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Database | MongoDB (pymongo) |
| AI/LLM | OpenAI API |
| Validation | Pydantic |
| Config | python-dotenv |

## Project Structure

```
adaptive-diagnostic-engine/
├── app/
│   ├── main.py            # FastAPI application entry point
│   ├── config.py          # Environment variable configuration
│   └── database.py        # MongoDB connection and collections
├── models/
│   ├── question.py        # Question schemas
│   └── session.py         # Session and result schemas
├── services/
│   ├── adaptive_engine.py # IRT algorithm and question selection
│   ├── question_service.py# Question CRUD operations
│   └── llm_service.py     # OpenAI study plan generation
├── routes/
│   ├── session_routes.py  # Session management endpoints
│   └── test_routes.py     # Testing and results endpoints
├── utils/
│   └── seed_questions.py  # Database seeding script
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start MongoDB

Make sure MongoDB is running locally on the default port:

```bash
# Using mongod directly
mongod --dbpath /data/db

# Or using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 3. Configure Environment Variables

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```
MONGODB_URI=mongodb://localhost:27017
DB_NAME=adaptive_diagnostic_engine
OPENAI_API_KEY=sk-your-actual-api-key
```

### 4. Seed the Database

```bash
python -m utils.seed_questions
```

This inserts 25 GRE-style questions across Algebra, Geometry, Vocabulary, and Reading.

### 5. Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## API Endpoints

### `POST /session/start`

Creates a new test session with an initial ability score of 0.5 and returns the first adaptively selected question.

**Response:**
```json
{
  "session_id": "uuid",
  "ability_score": 0.5,
  "question": {
    "id": "q1",
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "difficulty": 0.5,
    "topic": "Algebra"
  }
}
```

### `GET /next-question/{session_id}`

Returns the next adaptive question based on the current ability score.

**Response:**
```json
{
  "session_id": "uuid",
  "ability_score": 0.55,
  "questions_answered": 3,
  "question": { ... }
}
```

### `POST /submit-answer`

Submits an answer, updates the ability score, and returns the next question (or completion status).

**Request Body:**
```json
{
  "session_id": "uuid",
  "question_id": "q1",
  "answer": "5"
}
```

**Response:**
```json
{
  "correct": true,
  "new_ability_score": 0.5732,
  "questions_answered": 1,
  "completed": false,
  "next_question": { ... }
}
```

### `GET /results/{session_id}`

Returns the final test results including topic breakdown and an AI-generated 3-step study plan.

**Response:**
```json
{
  "session_id": "uuid",
  "final_ability_score": 0.6234,
  "total_correct": 7,
  "total_questions": 10,
  "topic_breakdown": {
    "Algebra": { "correct": 3, "total": 4 },
    "Geometry": { "correct": 1, "total": 2 }
  },
  "study_plan": [
    { "step": 1, "topic": "Geometry", "recommendation": "..." },
    { "step": 2, "topic": "Vocabulary", "recommendation": "..." },
    { "step": 3, "topic": "Test Strategy", "recommendation": "..." }
  ]
}
```

## Adaptive Algorithm

The engine uses a simplified **Item Response Theory (IRT)** model for 1-dimensional adaptive testing.

### Ability Update Formula

After each response, the ability score is updated:

```
probability = 1 / (1 + exp(-(ability - difficulty)))
ability_new = ability_old + 0.3 × (correct - probability)
```

Where:
- `ability` is the test-taker's current estimated ability (starts at 0.5)
- `difficulty` is the question's difficulty parameter (0.1 to 1.0)
- `correct` is 1 if the answer was correct, 0 otherwise
- `probability` is the model's predicted chance of a correct response
- `0.3` is the learning rate controlling update magnitude

### Question Selection

The next question is selected by finding the unanswered question whose difficulty is **closest** to the test-taker's current ability score. This ensures each question provides maximum information about the test-taker's ability level.

### Termination

The test ends after **10 questions**, at which point the session is marked complete and results become available.

## AI Log

This project was developed with the assistance of AI tools that accelerated the development process:

- **Architecture Design**: AI assisted in planning the modular project structure, ensuring clean separation between routes, services, and data layers.
- **IRT Algorithm**: AI helped implement the simplified Item Response Theory equations and validate the adaptive question selection logic.
- **Seed Data Generation**: AI accelerated creation of 25 GRE-style questions across four topics with calibrated difficulty values.
- **OpenAI Integration**: AI guided the structured prompt design for generating personalized study plans, including fallback handling for API failures.
- **Documentation**: AI generated comprehensive API documentation and algorithm explanations for this README.

These tools reduced development time while maintaining production-quality code standards. All generated code was reviewed and refined to ensure correctness, clean architecture, and adherence to Python best practices.
