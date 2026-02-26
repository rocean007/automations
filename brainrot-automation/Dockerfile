FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p /app/character_dataset \
    /app/generated_content \
    /app/output_videos \
    /app/music \
    /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CREATE_NOW=false

# Run the automation
CMD ["python", "main.py"]