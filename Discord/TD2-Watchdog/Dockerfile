FROM python:3.12-slim

# Don't write .pyc files; flush stdout/stderr immediately for clean logs.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code.
COPY bot.py .

# Watches are persisted here; mount a volume to keep them across restarts.
RUN mkdir -p /data
VOLUME ["/data"]

# Run as a non-root user.
RUN useradd --create-home --uid 1000 botuser && chown -R botuser:botuser /app /data
USER botuser

CMD ["python", "bot.py"]
