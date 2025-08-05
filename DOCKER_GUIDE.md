# 🐳 Docker Deployment Guide

## ✅ Lợi ích của Docker

- **Dễ deploy**: Chỉ cần 1 lệnh để chạy toàn bộ ứng dụng
- **Consistent**: Chạy giống nhau trên mọi môi trường
- **Isolated**: Không ảnh hưởng đến hệ thống host
- **Scalable**: Dễ dàng scale và deploy lên cloud

## 🚀 Quick Start

### Cách 1: Sử dụng script tự động
```bash
./docker-build.sh
```

### Cách 2: Build và run thủ công
```bash
# Build Docker image
docker build -t han-viet-translator .

# Run với docker-compose
docker-compose up -d
```

## 📋 Docker Commands

### Build Image
```bash
docker build -t han-viet-translator .
```

### Run Container
```bash
# Run với docker-compose (recommended)
docker-compose up -d

# Hoặc run trực tiếp
docker run -p 5008:5008 han-viet-translator
```

### View Logs
```bash
# Xem logs real-time
docker-compose logs -f

# Xem logs của container cụ thể
docker logs <container_id>
```

### Stop Application
```bash
# Stop với docker-compose
docker-compose down

# Hoặc stop container
docker stop <container_id>
```

### Remove Containers/Images
```bash
# Remove containers và volumes
docker-compose down -v

# Remove image
docker rmi han-viet-translator
```

## 🔧 Docker Configuration

### Dockerfile Features
- **Base Image**: Python 3.11-slim (nhẹ và an toàn)
- **Security**: Chạy với non-root user
- **Health Check**: Tự động kiểm tra sức khỏe app
- **Optimized**: Multi-stage build để giảm kích thước

### docker-compose.yml Features
- **Port Mapping**: 5008:5008
- **Volume Mounting**: Cache model files
- **Environment Variables**: Production settings
- **Health Check**: Auto-restart nếu app crash
- **Restart Policy**: unless-stopped

## 🌐 Access Application

Sau khi chạy thành công:
- **Web UI**: http://localhost:5008
- **Health Check**: http://localhost:5008/api/health
- **API Test**: 
```bash
curl -X POST http://localhost:5008/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "你好"}'
```

## 📊 Monitoring

### Container Status
```bash
# Xem status containers
docker-compose ps

# Xem resource usage
docker stats
```

### Logs Analysis
```bash
# Xem logs với timestamps
docker-compose logs -t

# Filter logs
docker-compose logs | grep "ERROR"
```

## 🚀 Deploy to Cloud

### Deploy to Render with Docker
1. Tạo **Web Service** trên Render
2. Connect với GitHub repository
3. Cấu hình:
   - **Build Command**: `docker build -t han-viet-translator .`
   - **Start Command**: `docker run -p $PORT:5008 han-viet-translator`
   - **Environment**: Docker

### Deploy to Heroku with Docker
1. Tạo `heroku.yml`:
```yaml
build:
  docker:
    web: Dockerfile
```
2. Deploy: `heroku container:push web`

### Deploy to AWS/GCP/Azure
- Sử dụng **Container Registry**
- Deploy với **Kubernetes** hoặc **ECS**
- Auto-scaling với **Load Balancer**

## 🛠️ Troubleshooting

### Build Issues
```bash
# Clean build
docker system prune -a
docker build --no-cache -t han-viet-translator .
```

### Port Conflicts
```bash
# Check port usage
lsof -i :5008

# Change port in docker-compose.yml
ports:
  - "8080:5008"  # Use port 8080 instead
```

### Memory Issues
```bash
# Increase memory limit
docker run -m 4g -p 5008:5008 han-viet-translator
```

### Model Download Issues
- Kiểm tra internet connection trong container
- Xem logs: `docker-compose logs -f`
- Model sẽ được tải tự động khi container start

## 📈 Performance Optimization

### Multi-stage Build
```dockerfile
# Build stage
FROM python:3.11-slim as builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
```

### Volume Caching
```yaml
volumes:
  - model_cache:/app/model_cache  # Cache model files
  - pip_cache:/root/.cache/pip    # Cache pip packages
```

## 🎉 Benefits Summary

✅ **Easy Deployment**: One command to run everything  
✅ **Consistent Environment**: Same behavior everywhere  
✅ **Resource Efficient**: Optimized image size  
✅ **Production Ready**: Health checks, logging, security  
✅ **Scalable**: Easy to deploy to any cloud platform  
✅ **Maintainable**: Clear separation of concerns  

Docker làm cho việc deploy trở nên đơn giản và chuyên nghiệp! 🐳 