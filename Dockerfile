# # Use official Python image
# FROM python:3.12-slim

# # Environment variables
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# # Set workdir
# WORKDIR /app

# # Install dependencies
# COPY requirements.txt .
# RUN pip install --upgrade pip \
#     && pip install -r requirements.txt

# # Copy project
# COPY . .

# # Create folder for static files
# RUN mkdir -p /app/staticfiles

# # Collect static files
# RUN python manage.py collectstatic --noinput

# # Run Gunicorn (WSGI)
# CMD ["gunicorn", "BackPage.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]


FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/staticfiles

CMD ["gunicorn", "BackPage.wsgi:application", "--bind", "0.0.0.0:9000", "--workers", "4"]
