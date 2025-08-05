# Hệ thống Dịch Hán-Việt

Ứng dụng web sử dụng AI để dịch và tìm kiếm câu từ tiếng Hán sang tiếng Việt.

## Tính năng

- Dịch câu tiếng Hán sang tiếng Việt
- Tìm kiếm thông minh sử dụng AI
- Giao diện web thân thiện
- API RESTful

## Công nghệ sử dụng

- **Backend**: Flask, Python
- **AI Models**: PhoBERT, LaBSE
- **Frontend**: HTML, CSS, JavaScript
- **Vector Search**: Sentence Transformers

## Deploy lên Render

### Bước 1: Chuẩn bị
1. Đảm bảo code đã được push lên GitHub
2. Có tài khoản Render (đăng ký tại https://render.com)

### Bước 2: Upload Model File
Trước khi deploy, bạn cần upload file `han_viet_vectorstore.pkl` lên nơi lưu trữ:

**Cách 1: Google Drive**
1. Upload file `han_viet_vectorstore.pkl` lên Google Drive
2. Share với "Anyone with the link"
3. Copy URL và thay thế `/view?usp=sharing` bằng `/uc?export=download`
4. Cập nhật URL trong file `download_model.py`

**Cách 2: File hosting service**
1. Upload lên https://file.io/ hoặc https://transfer.sh/
2. Copy direct download URL
3. Cập nhật URL trong file `download_model.py`

### Bước 3: Deploy trên Render
1. Đăng nhập vào Render Dashboard
2. Click "New +" → "Web Service"
3. Connect với GitHub repository
4. Cấu hình:
   - **Name**: han-viet-translator (hoặc tên bạn muốn)
   - **Environment**: Python 3
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

### Bước 3: Environment Variables (nếu cần)
Thêm các biến môi trường nếu cần:
- `PORT`: 10000 (Render sẽ tự động set)

### Bước 4: Deploy
Click "Create Web Service" và chờ deploy hoàn tất.

## Chạy locally

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy ứng dụng
python app.py
```

Truy cập: http://localhost:5008

## API Endpoints

- `GET /`: Trang chủ
- `POST /api/search`: Tìm kiếm/dịch câu Hán-Việt
- `GET /api/health`: Health check

## Cấu trúc project

```
├── app.py                 # Flask app chính
├── han_viet_search_system.py  # Logic AI
├── requirements.txt       # Python dependencies
├── Procfile              # Render configuration
├── runtime.txt           # Python version
├── templates/            # HTML templates
├── static/              # CSS, JS files
└── han_viet_vectorstore.pkl  # AI model data
```

## Lưu ý

- App sẽ sleep sau 15 phút không hoạt động (free tier)
- Lần đầu truy cập có thể chậm do cần load AI models
- File `han_viet_vectorstore.pkl` cần được upload lên Render 