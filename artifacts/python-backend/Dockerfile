FROM python:3.11-slim

# Prevent Python from writing .pyc files & enable logs instantly
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install minimal system dependencies (only what's needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip (IMPORTANT for large packages like torch)
RUN pip install --upgrade pip

# Copy only requirements first (better caching)
COPY requirements.txt .

# Install dependencies with increased timeout
RUN pip install --no-cache-dir --timeout 1000 -r requirements.txt

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run server (better than python main.py)
CMD ["python", "main.py"]