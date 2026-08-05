FROM python:3.11-slim

# Install system dependencies for ffmpeg + audio
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install python deps
COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot/ .

# Run the bot
CMD ["python", "main.py"]