FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libssl-dev \
    build-essential \
    wkhtmltopdf \
    && apt-get clean

# Set work directory
WORKDIR /app/

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Expose the port (informational)
EXPOSE 8000

# Default command (can be overridden in entrypoint.sh)
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
