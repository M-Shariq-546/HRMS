FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    gcc \
    wkhtmltopdf \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/

COPY package*.json ./

# Install npm dependencies
RUN npm install

COPY . .

# Build React components (doesn't need Python env vars)
RUN npm run build

RUN chmod +x /app/entrypoint.sh

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python3", "manage.py", "runserver"]
