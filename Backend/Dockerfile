FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (needed for some python packages like cv2 or build tools)
# Added unixodbc-dev for pyodbc support on Linux
RUN apt-get update && apt-get install -y \
    build-essential \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY Backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
# We copy the parent "App" directory into /app/App
# and "Backend" directory into /app/Backend
COPY App /app/App
COPY Backend /app/Backend

# Set PYTHONPATH to include /app so "from App... import ..." works
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the app from the Backend directory
WORKDIR /app/Backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]