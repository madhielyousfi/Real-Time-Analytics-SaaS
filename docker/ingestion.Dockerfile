FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY ingestion-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ingestion-service/ ./ingestion-service/
COPY shared/ ./shared/

ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["uvicorn", "ingestion-service.app.main:app", "--host", "0.0.0.0", "--port", "8001"]