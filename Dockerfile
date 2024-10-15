# Base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements/ /app/requirements/
RUN pip install --upgrade pip && pip install -r /app/requirements/production.txt

# Copy project
COPY . /app/

# Gunicorn port
EXPOSE 8000

# Daphne port (WebSocket)
EXPOSE 8001

# Run gunicorn and daphne
CMD ["bash", "-c", "gunicorn core.wsgi:application --bind 0.0.0.0:8000"]
