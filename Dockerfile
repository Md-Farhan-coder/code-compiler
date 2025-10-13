# Dockerfile
FROM ubuntu:24.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv python3-pip python3-dev build-essential g++ openjdk-17-jdk-headless \
    ca-certificates curl tzdata && \
    rm -rf /var/lib/apt/lists/*

# Create app user (avoid running as root)
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app
USER appuser

# Copy requirements and install
COPY --chown=appuser:appuser requirements.txt /home/appuser/app/
RUN python3 -m pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser main.py /home/appuser/app/

EXPOSE 8000

# Run using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
