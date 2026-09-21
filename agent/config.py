import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

GROQ_BASE_URL = os.getenv(
    "GROQ_BASE_URL",
    "https://api.groq.com/openai/v1"
)

SEARCH_RESULTS_PER_QUERY = int(
    os.getenv("SEARCH_RESULTS_PER_QUERY", "3")
)

SEARCH_TIMEOUT = int(
    os.getenv("SEARCH_TIMEOUT", "8")
)

REQUEST_TIMEOUT = int(
    os.getenv("REQUEST_TIMEOUT", "30")
)

MAX_RETRIES = int(
    os.getenv("MAX_RETRIES", "1")
)