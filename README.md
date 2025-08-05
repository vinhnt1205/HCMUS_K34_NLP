# Hệ thống Tìm kiếm Hán-Việt

Ứng dụng Flask API để tìm kiếm và dịch thuật văn bản Hán-Việt sử dụng các mô hình AI.

## Tính năng

- Tìm kiếm semantic cho văn bản Hán
- Dịch thuật Hán-Việt
- API RESTful
- Giao diện web
- Tối ưu hóa hiệu suất với vectorstore caching

## Cài đặt và Chạy với Docker

### 1. Build Docker Image

```bash
docker build -t han-viet-search .
```

### 2. Chạy với Docker Compose (Khuyến nghị)

```bash
docker-compose up -d
```

### 3. Chạy với Docker trực tiếp

```bash
docker run -d \
  --name han-viet-search-app \
  -p 5008:5008 \
  -v $(pwd)/models:/app/models \
  han-viet-search
```

## Sử dụng

### Truy cập Web Interface
```
http://localhost:5008
```

### API Endpoints

#### Health Check
```bash
curl http://localhost:5008/api/health
```

#### Tìm kiếm
```bash
curl -X POST http://localhost:5008/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "鎮驚安神"}'
```

#### Khởi tạo Model
```bash
curl http://localhost:5008/api/init-model
```

## Cấu trúc Project

```
.
├── app.py                          # Flask application
├── han_viet_search_system.py       # Core search system
├── download_model.py               # Model download utilities
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml             # Docker Compose configuration
├── .dockerignore                   # Docker ignore rules
├── templates/                      # HTML templates
├── static/                         # Static files (CSS, JS)
└── models/                         # Model files (mounted volume)
```

## Environment Variables

- `PYTHONPATH`: Path to Python modules
- `FLASK_APP`: Flask application file
- `FLASK_ENV`: Environment (production/development)
- `PORT`: Port number (default: 5008)

## Monitoring

### Health Check
Container có health check tự động kiểm tra trạng thái API mỗi 30 giây.

### Logs
```bash
# Xem logs
docker-compose logs -f

# Hoặc với Docker trực tiếp
docker logs -f han-viet-search-app
```

## Troubleshooting

### 1. Model không load được
```bash
# Kiểm tra API init-model
curl http://localhost:5008/api/init-model
```

### 2. Container không start
```bash
# Kiểm tra logs
docker logs han-viet-search-app
```

### 3. Memory issues
Tăng memory limit trong docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      memory: 8G
```

## Performance

- Vectorstore được load một lần khi khởi động
- Caching để tăng tốc độ phản hồi
- Memory optimization cho production

## Development

### Local Development
```bash
pip install -r requirements.txt
python app.py
```

### Rebuild Docker Image
```bash
docker-compose build --no-cache
docker-compose up -d
``` 