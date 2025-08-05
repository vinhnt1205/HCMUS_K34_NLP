# Hướng dẫn Deploy lên Render

## ✅ Chuẩn bị hoàn tất

Repository đã được chuẩn bị đầy đủ:
- ✅ File `.gitignore` loại trừ file `.pkl` (quá nặng)
- ✅ Script `download_model.py` tự động tải model từ Hugging Face Hub
- ✅ Script `build.sh` cấu hình cho Render
- ✅ File `requirements.txt` với tất cả dependencies
- ✅ File `Procfile` và `runtime.txt` cho Render

## 🚀 Deploy trên Render

### Bước 1: Đăng nhập Render
1. Truy cập [render.com](https://render.com)
2. Đăng nhập hoặc tạo tài khoản mới

### Bước 2: Tạo Web Service
1. Click "New +" → "Web Service"
2. Connect với GitHub repository: `https://github.com/vinhnt1205/K34_HCMUS_NLP`
3. Chọn branch `main`

### Bước 3: Cấu hình Service
```
Name: han-viet-translator
Environment: Python 3
Build Command: chmod +x build.sh && ./build.sh
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1
Plan: Free
```

**Hoặc sử dụng render.yaml (recommended):**
1. File `render.yaml` đã được tạo sẵn
2. Render sẽ tự động detect và sử dụng cấu hình này
3. Không cần cấu hình thủ công

### Bước 4: Environment Variables
Không cần thêm biến môi trường nào, Render sẽ tự động set `PORT`.

### Bước 5: Deploy
Click "Create Web Service" và chờ deploy hoàn tất.

## 📋 Quá trình Deploy

Render sẽ thực hiện các bước sau:

1. **Clone Repository**: Tải code từ GitHub
2. **Install Dependencies**: Chạy `pip install -r requirements.txt`
3. **Download Model**: Chạy `python3 download_model.py` để tải model từ Hugging Face Hub
4. **Start App**: Khởi động với `gunicorn app:app`

## 🔍 Kiểm tra Deploy

### Logs
- Theo dõi logs trong Render Dashboard
- Tìm kiếm thông báo "✅ Model downloaded successfully!"

### Test API
Sau khi deploy thành công, test API:
```bash
curl -X POST https://your-app-name.onrender.com/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "你好"}'
```

## ⚠️ Lưu ý quan trọng

### Free Tier Limitations
- App sẽ sleep sau 15 phút không hoạt động
- Lần đầu truy cập có thể chậm (30-60 giây) do cần load model
- Build time có thể lâu do cần tải model 2.3GB

### Model Download
- Model được tải từ Hugging Face Hub: `ntvinh12052001/han_viet_vectorstore`
- Nếu tải thất bại, script sẽ tạo dummy model để test
- File model không được commit lên GitHub (quá nặng)

## 🛠️ Troubleshooting

### Nếu deploy thất bại:
1. Kiểm tra logs trong Render Dashboard
2. Đảm bảo repository có đầy đủ file cần thiết
3. Kiểm tra `requirements.txt` có đúng dependencies

### Nếu model không tải được:
1. Kiểm tra kết nối internet
2. Script sẽ tạo dummy model để test
3. Kiểm tra URL Hugging Face Hub trong `download_model.py`

### Nếu app không start được:
1. Kiểm tra `Start Command` có đúng không
2. Đảm bảo `gunicorn` đã được cài đặt
3. Kiểm tra port configuration

## 📞 Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. Render Dashboard logs
2. GitHub repository: https://github.com/vinhnt1205/K34_HCMUS_NLP
3. Hugging Face dataset: https://huggingface.co/datasets/ntvinh12052001/han_viet_vectorstore

## 🎉 Thành công!

Sau khi deploy thành công, bạn sẽ có:
- ✅ Web app hoạt động tại `https://your-app-name.onrender.com`
- ✅ API endpoint cho tìm kiếm Hán-Việt
- ✅ Model AI tự động tải và hoạt động
- ✅ Giao diện web thân thiện 