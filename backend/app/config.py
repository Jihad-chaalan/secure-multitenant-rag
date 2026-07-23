import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent  # Goes up to backend folder
DATA_DIR = BASE_DIR / "app" / "data" / "documents"


# LLM Settings (Groq)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.2))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 1024))


# Optional: Support both OpenAI and Groq naming
OPENAI_API_KEY = GROQ_API_KEY  # For compatibility


CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))

# Embedding Settings 
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2


# VectorDB Settings 
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "enterprise_rag")


# Retrieval Settings
TOP_K = int(os.getenv("TOP_K", 5))

# Google Drive Settings
GDRIVE_ROOT_FOLDER_ID = os.getenv("GDRIVE_ROOT_FOLDER_ID", "")


# Reranker Settings (Cross-Encoder)
USE_RERANKER = os.getenv("USE_RERANKER", "true").lower() == "true"
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
RERANKER_TOP_K = int(os.getenv("RERANKER_TOP_K", 5))
RERANKER_CANDIDATE_COUNT = int(os.getenv("RERANKER_CANDIDATE_COUNT", 20))


# FastAPI Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

# AI Security Layer
ENABLE_AI_SECURITY_LAYER = os.getenv("ENABLE_AI_SECURITY_LAYER", "true").lower() == "true"