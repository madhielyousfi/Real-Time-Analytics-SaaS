FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY stream-processor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY stream-processor/ ./stream-processor/
COPY shared/ ./shared/
COPY backend/ ./backend/

ENV PYTHONPATH=/app

CMD ["python", "-m", "stream-processor.consumers.event_consumer"]