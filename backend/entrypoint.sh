#!/usr/bin/env sh
set -eu

# Run Alembic migrations automatically when PostgreSQL is configured
if [ -n "${DATABASE_URL:-}" ] || [ -n "${POSTGRES_HOST:-}" ]; then
  echo "[entrypoint] Applying Alembic database migrations..."
  alembic upgrade head
fi

PORT_TO_USE="${PORT:-${BACKEND_PORT:-8000}}"
WORKERS_TO_USE="${UVICORN_WORKERS:-1}"

echo "[entrypoint] Starting SkillGap AI FastAPI server on 0.0.0.0:${PORT_TO_USE} (workers=${WORKERS_TO_USE})"
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port "${PORT_TO_USE}" \
  --workers "${WORKERS_TO_USE}" \
  --proxy-headers \
  --forwarded-allow-ips="*"
