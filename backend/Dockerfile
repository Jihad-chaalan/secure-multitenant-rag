# backend/Dockerfile

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app \
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface \
    HF_HUB_DISABLE_SYMLINKS_WARNING=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch (CPU version)
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install all dependencies
RUN pip install --no-cache-dir \
    sentence-transformers \
    qdrant-client \
    google-api-python-client \
    google-auth-httplib2 \
    google-auth-oauthlib \
    pypdf \
    python-docx \
    langchain-text-splitters \
    fastapi \
    uvicorn \
    python-multipart \
    rank-bm25 \
    groq \
    httpx \
    python-dotenv

#  Pre-download the model during build
# This uses the HF_HOME environment variable set above
RUN python -c "import os; from sentence_transformers import SentenceTransformer; \
    print('Downloading model...'); \
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); \
    print('Model downloaded successfully to:', os.environ.get('HF_HOME', '/app/.cache/huggingface'))"

# Copy application code
COPY app/ /app/app/
COPY tests/ /app/tests/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]