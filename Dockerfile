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
# Configure Nginx - TEMPLATE (port injected at runtime)
# ============================================
RUN rm -f /etc/nginx/conf.d/default.conf
RUN rm -f /etc/nginx/sites-enabled/default
RUN rm -f /etc/nginx/sites-available/default

# NOTE: we deliberately do NOT touch the "include /etc/nginx/conf.d/*.conf;"
# line in nginx.conf — it must stay active so our rendered config loads.

RUN echo 'server { \
    listen PORT_PLACEHOLDER; \
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
}' > /etc/nginx/conf.d/default.conf.template

# ---- CRITICAL FIX: Heroku runs the container as a non-root, dynamically
# assigned user. Even though we're root during build, at runtime nginx
# cannot create NEW files in /etc/nginx/conf.d (root-owned, 755 by default).
# Pre-create the target file here (as root, at build time) and open up
# permissions so the runtime sed command can overwrite its CONTENTS
# (which only needs write access to the existing file, not the directory).
RUN touch /etc/nginx/conf.d/default.conf && \
    chmod 666 /etc/nginx/conf.d/default.conf && \
    mkdir -p /var/log/nginx /var/lib/nginx/body /var/lib/nginx/proxy /var/lib/nginx/fastcgi /var/lib/nginx/uwsgi /var/lib/nginx/scgi && \
    chmod -R 777 /var/log/nginx /var/lib/nginx && \
    chmod 777 /run 2>/dev/null || true

# ============================================
# Startup Script - Run Both Nginx and FastAPI
# ============================================
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "=============================================================="\n\
echo "🚀 Starting full application..."\n\
echo "📡 Nginx will serve frontend on port ${PORT:-8080}"\n\
echo "⚡ FastAPI will run on port 8000"\n\
echo "👤 Running as UID: $(id -u), GID: $(id -g)"\n\
echo "=============================================================="\n\
\n\
# Render nginx config with the Heroku-assigned $PORT (falls back to 8080 locally)\n\
sed "s/PORT_PLACEHOLDER/${PORT:-8080}/g" /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf\n\
\n\
echo "---- Rendered /etc/nginx/conf.d/default.conf ----"\n\
cat /etc/nginx/conf.d/default.conf\n\
echo "---------------------------------------------------"\n\
\n\
mkdir -p /tmp/nginx\n\
\n\
# Test nginx config; dump full merged config for visibility if it fails\n\
if ! nginx -t 2>&1; then\n\
    echo "❌ nginx config test failed. Full merged config dump:"\n\
    nginx -T 2>&1 || true\n\
    exit 1\n\
fi\n\
\n\
# Start Nginx with an explicit, writable pid path\n\
nginx -g "daemon off; pid /tmp/nginx/nginx.pid;" &\n\
\n\
# Wait for nginx to start\n\
sleep 2\n\
\n\
# Start FastAPI\n\
exec uvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/start.sh

RUN chmod +x /app/start.sh

# Expose ports (informational only — Heroku ignores this and injects $PORT)
EXPOSE 8080 8000

# Start both services
CMD ["/app/start.sh"]