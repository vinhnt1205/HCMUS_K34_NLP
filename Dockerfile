# Sử dụng Python 3.9 làm base image
FROM python:3.9-slim

# Thiết lập working directory
WORKDIR /app

# Cài đặt system dependencies cần thiết
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt trước để tận dụng Docker cache
COPY requirements.txt .

# Cài đặt Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code
COPY . .

# Tạo thư mục để lưu model nếu chưa có
RUN mkdir -p /app/models

# Expose port
EXPOSE 5008

# Thiết lập environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5008/api/health || exit 1

# Command để chạy ứng dụng
CMD ["python", "app.py"] 