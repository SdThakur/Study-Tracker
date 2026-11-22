# Dockerfile for Study Tracker API (Lesson 10)
FROM python:3.12-slim

WORKDIR /code

# Copy and install dependencies first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application code
COPY ./app ./app

EXPOSE 8000

# Run in production mode with 2 workers
CMD ["fastapi", "run", "app/main.py", "--port", "8000", "--workers", "2"]
