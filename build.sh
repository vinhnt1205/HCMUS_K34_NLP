#!/bin/bash
echo "=== Build Script for Render ==="

# Cài đặt dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Tạo lightweight model cho Render
echo "Creating lightweight model for Render..."
python3 -c "
import pandas as pd
import pickle

dummy_data = {
    'Câu tiếng Hán': ['你好', '谢谢', '再见', '一大熱傷血', '心無血養'],
    'translation': ['Xin chào', 'Cảm ơn', 'Tạm biệt', 'Một đại nhiệt thương huyết', 'Tâm vô huyết dưỡng'],
    'best_match': ['Xin chào', 'Cảm ơn', 'Tạm biệt', 'Một đại nhiệt thương huyết', 'Tâm vô huyết dưỡng']
}

df = pd.DataFrame(dummy_data)
vectorstore = {'df': df}

with open('han_viet_vectorstore.pkl', 'wb') as f:
    pickle.dump(vectorstore, f)

print('✅ Lightweight model created successfully!')
"

echo "=== Build completed successfully ===" 