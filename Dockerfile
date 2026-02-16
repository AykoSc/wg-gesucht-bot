FROM python:3.14-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install system dependencies needed for compiling lxml
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    libxml2-dev \
    libxslt-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and Firefox with ALL dependencies
RUN playwright install --with-deps firefox

# Create data directory
RUN mkdir data

# Copy project files
COPY . .

# Create empty past_listings.txt and debug.log if they don't exist
RUN touch past_listings.txt debug.log

# Run the bot
CMD ["python", "main.py"]
