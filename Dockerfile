# Sử dụng Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directory for model files
RUN mkdir -p /app/models

# Download model file during build (optional - can also download at runtime)
# RUN python download_model.py

# Expose port
EXPOSE 5008

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:64
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5008/api/health || exit 1

# Run the application
CMD ["python", "app.py"] 