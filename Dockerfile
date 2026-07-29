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
# Nginx: FULLY SELF-CONTAINED CONFIG
# ============================================
# We deliberately do NOT use /etc/nginx/nginx.conf, conf.d/, or
# sites-enabled/ at all. The Debian nginx package ships a default
# config chain that, in Heroku's non-root runtime, was causing nginx
# to attempt binding port 80 from a source we could not fully isolate.
# Instead we give nginx ONE explicit, complete config file via `-c`,
# which nginx uses exclusively -- nothing else on disk is consulted.
# Verified working as a non-root user on an arbitrary high port.
RUN mkdir -p /app/nginx/body /app/nginx/proxy /app/nginx/fastcgi \
    /app/nginx/uwsgi /app/nginx/scgi /app/nginx/logs && \
    chmod -R 777 /app/nginx

RUN echo 'worker_processes auto; \
pid /app/nginx/nginx.pid; \
error_log /app/nginx/logs/error.log; \
\
events { \
    worker_connections 768; \
} \
\
http { \
    include /etc/nginx/mime.types; \
    default_type application/octet-stream; \
    access_log /app/nginx/logs/access.log; \
    client_body_temp_path /app/nginx/body; \
    proxy_temp_path /app/nginx/proxy; \
    fastcgi_temp_path /app/nginx/fastcgi; \
    uwsgi_temp_path /app/nginx/uwsgi; \
    scgi_temp_path /app/nginx/scgi; \
\
    server { \
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
    } \
}' > /app/nginx/nginx.conf.template

RUN touch /app/nginx/nginx.conf && chmod 666 /app/nginx/nginx.conf

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
# Render self-contained nginx config with the Heroku-assigned $PORT\n\
sed "s/PORT_PLACEHOLDER/${PORT:-8080}/g" /app/nginx/nginx.conf.template > /app/nginx/nginx.conf\n\
\n\
echo "---- Rendered /app/nginx/nginx.conf ----"\n\
cat /app/nginx/nginx.conf\n\
echo "---------------------------------------------------"\n\
\n\
# Test config (self-contained: -c points directly at our file, no system\n\
# nginx.conf / conf.d / sites-enabled is consulted at all)\n\
if ! nginx -t -c /app/nginx/nginx.conf 2>&1; then\n\
    echo "❌ nginx config test failed"\n\
    exit 1\n\
fi\n\
\n\
# Start Nginx with our self-contained config\n\
nginx -c /app/nginx/nginx.conf &\n\
\n\
# Wait for nginx to start\n\
sleep 2\n\
\n\
# Start FastAPI\n\
exec uvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/start.sh

RUN chmod +x /app/start.sh

# Expose ports (informational only -- Heroku ignores this and injects $PORT)
EXPOSE 8080 8000

# Start both services
CMD ["/app/start.sh"]