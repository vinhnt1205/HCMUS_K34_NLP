#!/bin/bash
echo "=== Build Script for Render ==="

# Cài đặt dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Tải model trước khi khởi động app
echo "Downloading model from Hugging Face Hub..."
python3 download_model.py

# Kiểm tra xem model đã tải thành công chưa
if [ -f "han_viet_vectorstore.pkl" ]; then
    file_size=$(ls -lh han_viet_vectorstore.pkl | awk '{print $5}')
    echo "✅ Model downloaded successfully! Size: $file_size"
else
    echo "⚠️  Model download failed, will create dummy model on startup"
    echo "This is normal for first deployment on Render"
fi

echo "=== Build completed successfully ===" 