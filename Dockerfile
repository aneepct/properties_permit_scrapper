# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=permit_api.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create non-root user first
RUN adduser --disabled-password --gecos '' appuser

# Create directories for logs, static files, and temp with proper permissions
RUN mkdir -p /app/logs /app/staticfiles /app/media /app/temp \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Collect static files as appuser
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--worker-class", "sync", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "permit_api.wsgi:application"]