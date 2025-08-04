# Hệ thống dịch Hán-Việt

Ứng dụng web dịch câu tiếng Hán sang tiếng Việt sử dụng AI và machine learning.

## Cài đặt và chạy với Docker

### Yêu cầu
- Docker
- Docker Compose

### Cách 1: Sử dụng Docker Compose (Khuyến nghị)

```bash
# Build và chạy ứng dụng
docker-compose up --build

# Chạy ở background
docker-compose up -d --build

# Dừng ứng dụng
docker-compose down
```

### Cách 2: Sử dụng Docker trực tiếp

```bash
# Build image
docker build -t han-viet-app .

# Chạy container
docker run -p 5008:5008 han-viet-app

# Chạy ở background
docker run -d -p 5008:5008 --name han-viet-container han-viet-app
```

## Truy cập ứng dụng

Sau khi chạy thành công, truy cập:
- **Web UI**: http://localhost:5008
- **Health Check**: http://localhost:5008/api/health

## API Endpoints

- `GET /` - Trang chủ
- `POST /api/search` - Tìm kiếm và dịch
- `GET /api/health` - Kiểm tra trạng thái

### Ví dụ sử dụng API

```bash
curl -X POST http://localhost:5008/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "你好世界"}'
```

## Cấu trúc thư mục

```
.
├── app.py                          # Flask application
├── han_viet_search_system.py       # Core search logic
├── han_viet_vectorstore.pkl        # Pre-trained model data
├── static/                         # CSS, JS files
├── templates/                      # HTML templates
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml             # Docker Compose config
└── README.md                      # This file
```

## Troubleshooting

### Lỗi port đã được sử dụng
```bash
# Kiểm tra port 5008
lsof -i :5008

# Kill process nếu cần
kill -9 <PID>
```

### Lỗi Docker build
```bash
# Xóa cache và build lại
docker system prune -a
docker build --no-cache -t han-viet-app .
```

### Xem logs
```bash
# Với Docker Compose
docker-compose logs -f

# Với Docker
docker logs han-viet-container
``` 