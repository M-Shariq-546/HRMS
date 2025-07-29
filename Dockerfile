# --------- Stage 1: React Build ---------
FROM node:18 AS frontend-builder

WORKDIR /app

# Copy only frontend source and package files
COPY HRMS/package*.json ./
COPY HRMS/webpack.config.js ./
COPY HRMS/static/src/ static/src/

# Install deps and build
RUN npm install
RUN npm run build

# --------- Stage 2: Python Backend ---------
FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    gcc \
    wkhtmltopdf \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy entire backend
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy built React assets from previous stage
COPY --from=frontend-builder /app/static/dist/ HRMS/static/dist/

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
