FROM python:3.11-alpine

WORKDIR /app

# Install system dependencies
RUN apk update && apk add --no-cache \
    gcc \
    g++ \
    postgresql-client \
    postgresql-dev \
    musl-dev

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user
RUN adduser -D -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Start script: wait for DB, run migrations, start uvicorn
# Arguments from docker-compose command will be passed to uvicorn
CMD sh -c "echo 'Starting Blog API...' && \
           echo 'Checking database connection...' && \
           python wait-for-db.py && \
           echo 'Running database migrations...' && \
           alembic upgrade head && \
           echo 'Starting uvicorn server...' && \
           exec uvicorn src.main:app --host 0.0.0.0 --port 8000 ${UVICORN_ARGS:-}"
