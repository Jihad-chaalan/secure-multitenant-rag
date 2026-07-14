import os
from dotenv import load_dotenv

load_dotenv()


# LLM Settings (Groq)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.2))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 1024))


# Optional: Support both OpenAI and Groq naming
OPENAI_API_KEY = GROQ_API_KEY  # For compatibility


CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
