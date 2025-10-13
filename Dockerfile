# Use official Python image
FROM python:3.11-slim

# Install compilers for C++ and Java
RUN apt-get update && apt-get install -y \
    g++ \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
