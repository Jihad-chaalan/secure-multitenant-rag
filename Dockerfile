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
# STAGE 2: Build Backend
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

# Install system dependencies (including nginx)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    ca-certificates \
    nginx \
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

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist /var/www/html

# ============================================
# Configure Nginx - FIXED!
# ============================================
RUN echo 'server { \
    listen 8080; \
    server_name _; \
    \
    location / { \
        root /var/www/html; \
        try_files $uri /index.html; \
    } \
    \
    location /api { \
        proxy_pass http://localhost:8000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
    \
    location /api/v1 { \
        proxy_pass http://localhost:8000/api/v1; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
    \
    location /docs { \
        proxy_pass http://localhost:8000/docs; \
        proxy_set_header Host $host; \
    } \
    \
    location /openapi.json { \
        proxy_pass http://localhost:8000/openapi.json; \
        proxy_set_header Host $host; \
    } \
}' > /etc/nginx/conf.d/default.conf

# ============================================
# Startup Script - FIXED!
# ============================================
RUN echo '#!/bin/bash\n\
echo "=============================================================="\n\
echo "🚀 Starting combined application..."\n\
echo "📡 Nginx will serve frontend on port 8080"\n\
echo "⚡ FastAPI will run on port 8000"\n\
echo "=============================================================="\n\
\n\
# Start Nginx in background\n\
nginx -g "daemon off;" &\n\
\n\
# Start FastAPI\n\
uvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/start.sh

RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 8080 8000

# Start both services
CMD ["/app/start.sh"]