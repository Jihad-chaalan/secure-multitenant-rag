# ============================================
# STAGE 1: Build Frontend with Build Args
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Build argument to control API URL
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=$VITE_API_URL

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source code
COPY frontend/ ./

# Build with the specified API URL
RUN npm run build

# ============================================
# STAGE 2: Build Backend (FastAPI Only)
# ============================================
FROM python:3.12-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app \
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface \
    HF_HUB_DISABLE_SYMLINKS_WARNING=1 \
    HF_HUB_ENABLE_HF_TRANSFER=1

WORKDIR /app

# Install system dependencies (no nginx needed)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch (CPU version)
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir

# Copy backend dependency files
COPY backend/pyproject.toml backend/uv.lock* ./

# Install Python dependencies
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

# Pre-download models
RUN python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; \
    print('📥 Downloading embedding model...'); \
    SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); \
    print('📥 Downloading reranker model...'); \
    CrossEncoder('cross-encoder/ms-marco-MiniLM-L6-v2'); \
    print('✅ All models downloaded successfully!')"

# Copy backend application code
COPY backend/app/ /app/app/
COPY backend/tests/ /app/tests/

# Copy built frontend (will be served separately later)
COPY --from=frontend-builder /app/frontend/dist /var/www/html

# ============================================
# Startup Script - FastAPI with Heroku PORT
# ============================================
RUN echo '#!/bin/bash\n\
echo "=============================================================="\n\
echo "🚀 Starting FastAPI backend..."\n\
echo "⚡ API will run on port ${PORT:-8000}"\n\
echo "=============================================================="\n\
\n\
# Use PORT from Heroku or default to 8000\n\
PORT=${PORT:-8000}\n\
\n\
# Start FastAPI on the correct port\n\
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT' > /app/start.sh

RUN chmod +x /app/start.sh

# Start FastAPI
CMD ["/app/start.sh"]