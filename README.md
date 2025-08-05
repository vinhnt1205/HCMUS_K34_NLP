# Hệ thống Dịch Hán-Việt

Ứng dụng web sử dụng AI để dịch và tìm kiếm câu từ tiếng Hán sang tiếng Việt.

## Tính năng

* Dịch câu tiếng Hán sang tiếng Việt
* Tìm kiếm thông minh sử dụng AI
* Giao diện web thân thiện
* API RESTful

## Công nghệ sử dụng

* **Backend**: Flask, Python
* **AI Models**: PhoBERT, LaBSE
* **Frontend**: HTML, CSS, JavaScript
* **Vector Search**: Sentence Transformers

## Deploy lên Render

### Bước 1: Chuẩn bị Repository

Repository đã được chuẩn bị sẵn với:
- ✅ File `.gitignore` loại trừ file `.pkl` (quá nặng)
- ✅ Script `download_model.py` tự động tải model từ Hugging Face Hub
- ✅ Script `build.sh` cấu hình cho Render
- ✅ File `requirements.txt` với tất cả dependencies

### Bước 2: Deploy trên Render

1. **Đăng nhập Render**: Truy cập [render.com](https://render.com) và đăng nhập

2. **Tạo Web Service**:
   - Click "New +" → "Web Service"
   - Connect với GitHub repository: `https://github.com/vinhnt1205/K34_HCMUS_NLP`

3. **Cấu hình Service**:
   - **Name**: `han-viet-translator` (hoặc tên bạn muốn)
   - **Environment**: `Python 3`
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

4. **Environment Variables** (nếu cần):
   - `PORT`: Render sẽ tự động set

5. **Deploy**: Click "Create Web Service"

### Bước 3: Quá trình Deploy

Render sẽ:
1. Clone repository từ GitHub
2. Chạy `build.sh` để:
   - Cài đặt dependencies từ `requirements.txt`
   - Tải model từ Hugging Face Hub
3. Khởi động app với Gunicorn

### Bước 4: Truy cập App

Sau khi deploy thành công, bạn sẽ nhận được URL như:
`https://han-viet-translator.onrender.com`

## Chạy locally

### Cách 1: Sử dụng Docker (Recommended)
```bash
# Build và run với Docker
./docker-build.sh

# Hoặc thủ công
docker build -t han-viet-translator .
docker-compose up -d
```

### Cách 2: Chạy trực tiếp
```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Tải model (tự động chạy khi start app)
python download_model.py

# Chạy ứng dụng
python app.py
```

Truy cập: http://localhost:5008

## API Endpoints

* `GET /`: Trang chủ
* `POST /api/search`: Tìm kiếm/dịch câu Hán-Việt
* `GET /api/health`: Health check
* `GET /api/init-model`: Khởi tạo model

## Cấu trúc project

```
├── app.py                 # Flask app chính
├── han_viet_search_system.py  # Logic AI
├── download_model.py      # Script tải model
├── build.sh              # Script build cho Render
├── requirements.txt      # Python dependencies
├── Procfile             # Render configuration
├── runtime.txt          # Python version
├── templates/           # HTML templates
├── static/             # CSS, JS files
└── .gitignore          # Loại trừ file .pkl
```

## Lưu ý quan trọng

* ✅ File `han_viet_vectorstore.pkl` được tải tự động từ Hugging Face Hub
* ✅ App sẽ sleep sau 15 phút không hoạt động (free tier)
* ✅ Lần đầu truy cập có thể chậm do cần load AI models
* ✅ Model được validate trước khi sử dụng

## Troubleshooting

### Nếu deploy thất bại:
1. Kiểm tra logs trong Render Dashboard
2. Đảm bảo repository có đầy đủ file cần thiết
3. Kiểm tra `requirements.txt` có đúng dependencies

### Nếu model không tải được:
1. Kiểm tra kết nối internet
2. Script sẽ tạo dummy model để test
3. Kiểm tra URL Hugging Face Hub trong `download_model.py`

## Liên hệ

Repository: [https://github.com/vinhnt1205/K34_HCMUS_NLP](https://github.com/vinhnt1205/K34_HCMUS_NLP) 