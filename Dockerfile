FROM python:3.11-slim

# Install ffmpeg for pydub/gTTS
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy everything
COPY .

# Install python packages
RUN pip install --no-cache-dir -r bot/requirements.txt

# Start the bot
CMD ["python", "bot/main.py"]