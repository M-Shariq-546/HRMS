FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED=1

# Install OS dependencies and Node.js 18 from NodeSource properly
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    ca-certificates \
    gcc \
    libcairo2-dev \
    wkhtmltopdf

# Add NodeSource Node.js 18 repo and install
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app/

# Copy only package.json and install JS dependencies
COPY package*.json ./
RUN npm install

# Copy rest of the app
COPY . .

# Build React components
RUN npm run build

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Install Python requirements
RUN pip install --no-cache-dir -r requirements.txt

# Expose Django default port
EXPOSE 8000

# Run Django
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
