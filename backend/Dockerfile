# Python Backend Dockerfile for Gridbricks Energy Procurement Analytics
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and pre-cached real January 2026 Elexon data
COPY app/ ./app/
COPY data/ ./data/
COPY run.py .

EXPOSE 8000

ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]
