# syntax=docker/dockerfile:1

# ===== Builder stage =====
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip wheel --wheel-dir=/wheels -r requirements.txt

# ===== Final stage =====
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings \
    PATH="/home/app/.local/bin:$PATH"

# Create non-root user
RUN useradd -m app && mkdir -p /app /staticfiles /media && chown -R app:app /app /staticfiles /media

WORKDIR /app

# System deps (minimal for SQLite)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
  && rm -rf /var/lib/apt/lists/*

# Install wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r /wheels/requirements.txt || true
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app

# Set production environment
ENV DJANGO_SETTINGS_MODULE=config.settings \
    STATIC_URL=/static/ \
    STATIC_ROOT=/staticfiles \
    MEDIA_ROOT=/media

# Create necessary directories
RUN mkdir -p /staticfiles /media /logs && \
    chown -R app:app /staticfiles /media /logs

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose app port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/quotes/')" || exit 1

USER app

# Start with startup script
CMD ["/app/scripts/start.sh"]