# Backend image, for hosting outside Vercel (any Docker host). On Vercel the
# backend runs as a Python function instead: see vercel.json.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.2.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

# Poetry installs the dependencies straight into the image's Python.
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root && rm -rf /root/.cache

COPY app ./app
COPY content ./content
# Seed for the persistent volume mounted on /app/storage (see entrypoint).
COPY storage ./seed/storage
COPY docker-entrypoint.sh ./

# Writable whatever user the platform runs the container as.
RUN mkdir -p /app/storage /app/.chroma \
    && chmod 777 /app/storage /app/.chroma \
    && chmod +x /app/docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/docker-entrypoint.sh"]
# --proxy-headers: the visitor's address comes from X-Forwarded-For, which
# the per-visitor chat rate limit relies on.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
