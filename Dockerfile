FROM python:3.11-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /code/

# Create logs directory
RUN mkdir -p /code/logs

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]