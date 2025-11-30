FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project into image
COPY . .

# Ensure entrypoint is executable inside the image (entrypoint will be mounted to /app)
RUN if [ -f /app/entrypoint.sh ]; then chmod +x /app/entrypoint.sh; fi

# Add /app/apps to PYTHONPATH if needed, but we set it in settings.py
# However, running from /app means manage.py is at /app/manage.py

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
