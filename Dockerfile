FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Set non-interactive frontend to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages safely
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        g++ \
        default-jdk \
        curl \
        wget \
        ca-certificates \
        unzip \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for Render
EXPOSE 8080

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
