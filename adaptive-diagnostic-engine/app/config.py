import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "adaptive_diagnostic_engine")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
