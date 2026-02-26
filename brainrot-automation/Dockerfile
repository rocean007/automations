FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/character_dataset \
    /app/generated_content \
    /app/output_videos \
    /app/music \
    /app/logs

ENV PYTHONUNBUFFERED=1
ENV CREATE_NOW=false

CMD ["python", "main.py"]
