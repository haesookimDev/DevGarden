FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file and create minimal package stub for editable install
COPY pyproject.toml .
RUN mkdir -p app && touch app/__init__.py

# Install Python dependencies (editable install for module resolution)
RUN pip install --no-cache-dir -e .

# Copy application code (overlays the stub)
COPY . .

# Run database migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
