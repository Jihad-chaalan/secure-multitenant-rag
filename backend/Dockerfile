# backend/Dockerfile

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

#  Install CPU-only PyTorch FIRST (prevents GPU version from being pulled in)
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies (removed chromadb, added qdrant-client)
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
    httpx2

# Copy application code
COPY app/ /app/app/
COPY tests/ /app/tests/

# Create a non-root user for security 
# RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
# USER appuser

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]