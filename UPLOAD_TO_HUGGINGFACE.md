# Hướng dẫn Upload file .pkl lên Hugging Face Hub

## Bước 1: Tạo tài khoản Hugging Face
1. Truy cập https://huggingface.co/
2. Đăng ký tài khoản mới

## Bước 2: Tạo Repository
1. Click "New Model" hoặc "New Dataset"
2. Chọn "Dataset" (vì file .pkl là data)
3. Đặt tên: `han-viet-model`
4. Chọn "Public" để có thể download mà không cần login

## Bước 3: Upload file
1. Vào repository vừa tạo
2. Click "Files and versions"
3. Click "Add file" → "Upload files"
4. Upload file `han_viet_vectorstore.pkl`
5. Commit changes

## Bước 4: Lấy URL
Sau khi upload, URL sẽ có dạng:
```
https://huggingface.co/datasets/YOUR_USERNAME/han-viet-model/resolve/main/han_viet_vectorstore.pkl
```

## Bước 5: Cập nhật code
Thay đổi URL trong file `download_model.py`:
```python
hf_url = "https://huggingface.co/datasets/YOUR_USERNAME/han-viet-model/resolve/main/han_viet_vectorstore.pkl"
```

## Lợi ích của Hugging Face Hub:
- ✅ Không có virus scan warning
- ✅ Download nhanh và ổn định
- ✅ Hỗ trợ file lớn
- ✅ Miễn phí
- ✅ Không cần authentication cho public files 