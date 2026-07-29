# ============================================
# Configure Nginx - TEMPLATE (port injected at runtime)
# ============================================
RUN rm -f /etc/nginx/conf.d/default.conf
RUN rm -f /etc/nginx/sites-enabled/default
RUN rm -f /etc/nginx/sites-available/default

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
# Startup Script
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
# Render nginx config with the Heroku-assigned $PORT\n\
sed "s/PORT_PLACEHOLDER/${PORT:-8080}/g" /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf\n\
\n\
echo "---- Rendered /etc/nginx/conf.d/default.conf ----"\n\
cat /etc/nginx/conf.d/default.conf\n\
echo "---------------------------------------------------"\n\
\n\
# Use a pid file location guaranteed to be writable by any user\n\
mkdir -p /tmp/nginx\n\
\n\
# Test nginx config, dump full merged config for visibility if it fails\n\
if ! nginx -t 2>&1; then\n\
    echo "❌ nginx config test failed. Full merged config dump:"\n\
    nginx -T 2>&1 || true\n\
    exit 1\n\
fi\n\
\n\
# Start Nginx with an explicit, writable pid path\n\
nginx -g "daemon off; pid /tmp/nginx/nginx.pid;" &\n\
\n\
sleep 2\n\
\n\
# Start FastAPI\n\
exec uvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 8080 8000

CMD ["/app/start.sh"]