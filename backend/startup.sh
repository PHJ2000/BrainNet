#!/bin/bash
set -euo pipefail

echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h db -U brain -d brainshare; do
  sleep 1
done

echo "Running alembic upgrade head..."
poetry run alembic upgrade head

echo "Starting server..."
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
