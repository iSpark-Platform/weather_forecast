FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Environment variables
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["gunicorn", "app:app", "--workers=2", "--threads=4", "--timeout=120", "--bind=0.0.0.0:5000"]
