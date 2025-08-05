# Hán-Việt Search System

Hệ thống tìm kiếm và dịch thuật Hán-Việt sử dụng AI, đặc biệt cho y học cổ truyền.

## Tính năng

- Tìm kiếm và dịch thuật câu tiếng Hán sang tiếng Việt
- Sử dụng Sentence Transformers và Transformers
- API RESTful với Flask
- Giao diện web thân thiện

## Cài đặt

### Local Development

1. Clone repository:
```bash
git clone <repository-url>
cd CK_2
```

2. Tạo virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

3. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

4. Chạy ứng dụng:
```bash
python app.py
```

Ứng dụng sẽ chạy tại `http://localhost:5008`

## Deployment trên Render

### Cách 1: Sử dụng render.yaml (Recommended)

1. Push code lên GitHub
2. Kết nối repository với Render
3. Render sẽ tự động detect `render.yaml` và deploy

### Cách 2: Manual Setup

1. Tạo Web Service trên Render
2. Connect với GitHub repository
3. Cấu hình:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Environment Variables**:
     - `PYTHON_VERSION`: `3.11`
     - `PORT`: `5008`

## API Endpoints

### Health Check
```
GET /api/health
```

### Search
```
POST /api/search
Content-Type: application/json

{
  "query": "你好"
}
```

### Initialize Model
```
GET /api/init-model
```

## Cấu trúc dự án

```
CK_2/
├── app.py                 # Flask application
├── han_viet_search_system.py  # Core search logic
├── download_model.py      # Model download utility
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── render.yaml           # Render deployment config
├── static/               # Static files (CSS, JS)
├── templates/            # HTML templates
└── han_viet_vectorstore.pkl  # Model file (2.36GB)
```

## Dependencies

- Flask==2.3.3
- Flask-Cors==4.0.0
- requests==2.31.0
- pandas==2.0.3
- torch==2.0.1
- numpy==1.24.3
- sentence-transformers==2.2.2
- transformers==4.30.2

## Lưu ý

- Model file (2.36GB) sẽ được tự động download từ Hugging Face Hub
- Cần ít nhất 4GB RAM để chạy ứng dụng
- Build time có thể mất 10-15 phút do download model file 