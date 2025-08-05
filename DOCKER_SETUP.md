# 🐳 Docker Setup Guide

## 📋 Prerequisites

### 1. Cài đặt Docker Desktop
- **macOS**: Tải từ [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Windows**: Tải từ [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: Cài đặt Docker Engine

### 2. Khởi động Docker
```bash
# macOS/Windows: Mở Docker Desktop app
# Linux: Start Docker service
sudo systemctl start docker
```

### 3. Kiểm tra cài đặt
```bash
docker --version
docker-compose --version
```

## 🚀 Quick Start với Docker

### Bước 1: Clone Repository
```bash
git clone https://github.com/vinhnt1205/K34_HCMUS_NLP.git
cd K34_HCMUS_NLP
```

### Bước 2: Build và Run
```bash
# Cách 1: Sử dụng script tự động
./docker-build.sh

# Cách 2: Build thủ công
docker build -t han-viet-translator .
docker-compose up -d
```

### Bước 3: Truy cập ứng dụng
- **Web UI**: http://localhost:5008
- **API Test**: 
```bash
curl -X POST http://localhost:5008/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "你好"}'
```

## 🔧 Docker Commands

### Build Image
```bash
docker build -t han-viet-translator .
```

### Run Container
```bash
# Với docker-compose (recommended)
docker-compose up -d

# Hoặc run trực tiếp
docker run -p 5008:5008 han-viet-translator
```

### View Logs
```bash
# Real-time logs
docker-compose logs -f

# Container logs
docker logs <container_id>
```

### Stop Application
```bash
docker-compose down
```

### Clean Up
```bash
# Remove containers và volumes
docker-compose down -v

# Remove images
docker rmi han-viet-translator

# Clean all unused resources
docker system prune -a
```

## 🛠️ Troubleshooting

### Docker daemon not running
```bash
# macOS/Windows: Mở Docker Desktop
# Linux: Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

### Port already in use
```bash
# Check port usage
lsof -i :5008

# Kill process using port
sudo kill -9 <PID>

# Hoặc change port trong docker-compose.yml
ports:
  - "8080:5008"
```

### Permission denied
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

### Build fails
```bash
# Clean build
docker system prune -a
docker build --no-cache -t han-viet-translator .
```

### Memory issues
```bash
# Increase memory limit
docker run -m 4g -p 5008:5008 han-viet-translator
```

## 📊 Monitoring

### Container Status
```bash
# List running containers
docker ps

# List all containers
docker ps -a

# Resource usage
docker stats
```

### Logs Analysis
```bash
# View logs with timestamps
docker-compose logs -t

# Filter error logs
docker-compose logs | grep "ERROR"

# Follow logs
docker-compose logs -f
```

## 🚀 Deploy to Cloud

### Render with Docker
1. Tạo **Web Service** trên Render
2. Connect với GitHub repository
3. Cấu hình:
   - **Build Command**: `docker build -t han-viet-translator .`
   - **Start Command**: `docker run -p $PORT:5008 han-viet-translator`
   - **Environment**: Docker

### Heroku with Docker
1. Tạo `heroku.yml`:
```yaml
build:
  docker:
    web: Dockerfile
```
2. Deploy:
```bash
heroku container:push web
heroku container:release web
```

### AWS/GCP/Azure
- **Container Registry**: Push image
- **Kubernetes/ECS**: Deploy containers
- **Load Balancer**: Auto-scaling

## 📈 Performance Tips

### Optimize Image Size
```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
```

### Use Volume Caching
```yaml
volumes:
  - model_cache:/app/model_cache
  - pip_cache:/root/.cache/pip
```

### Health Checks
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5008/api/health || exit 1
```

## 🎉 Benefits

✅ **Easy Setup**: One command to run everything  
✅ **Consistent**: Same environment everywhere  
✅ **Isolated**: No conflicts with host system  
✅ **Scalable**: Easy to deploy to cloud  
✅ **Maintainable**: Clear separation of concerns  
✅ **Production Ready**: Health checks, logging, security  

Docker làm cho việc development và deployment trở nên đơn giản! 🐳 