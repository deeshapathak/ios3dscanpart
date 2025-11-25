FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for Open3D
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY mesh_cleanup_api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY mesh_cleanup_api/main.py .

# Expose port
EXPOSE 8000

# Run the application
# Render sets PORT automatically, but uvicorn will use it from environment
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

