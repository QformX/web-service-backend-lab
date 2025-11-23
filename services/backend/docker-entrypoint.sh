#!/bin/bash
set -e

echo "Starting Blog API..."

# Wait for database to be ready
echo "Checking database connection..."
python wait-for-db.py

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting uvicorn server..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 "$@"

