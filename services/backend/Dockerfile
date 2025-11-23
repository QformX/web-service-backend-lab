FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Convert line endings (CRLF to LF) and make scripts executable
# This ensures compatibility between Windows and Unix-based systems
RUN sed -i 's/\r$//' docker-entrypoint.sh && \
    sed -i 's/\r$//' wait-for-db.py && \
    chmod +x docker-entrypoint.sh && \
    chmod +x wait-for-db.py

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]

# Default command (can be overridden)
CMD []
