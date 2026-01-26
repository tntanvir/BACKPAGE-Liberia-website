
# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
# ffmpeg is required for yt-dlp to merge video/audio
# libpq-dev and gcc are often needed for psycopg2 if postgres is used later
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Expose port (documentary)
# Expose port (documentary)
EXPOSE 9000

# Run entrypoint script (optional, but good for migrations)
# We will define the actual command in docker-compose
CMD ["python", "manage.py", "runserver", "0.0.0.0:9000"]
