FROM python:3.13-slim

WORKDIR /app

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV DATABASE_URL=sqlite:////data/sitecare.db
ENV PORT=8000

# Ensure data dir exists
RUN mkdir -p /data

EXPOSE 8000
CMD sh -c "python3 -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
