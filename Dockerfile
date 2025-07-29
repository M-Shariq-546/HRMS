FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    gcc \
    wkhtmltopdf \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package*.json ./
COPY . .

RUN npm install
RUN npm run build  # Build React app (ensure Webpack writes to static/dist)

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["gunicorn", "horilla.wsgi:application", "--bind", "0.0.0.0:8000"]
