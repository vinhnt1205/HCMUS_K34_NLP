#!/usr/bin/env python3
"""
Script để tạo model từ CSV thay vì download file .pkl lớn
"""

import os
import pickle
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import torch

def validate_pickle_file(file_path):
    """Kiểm tra xem file có phải là pickle hợp lệ không"""
    try:
        with open(file_path, 'rb') as f:
            # Đọc 4 bytes đầu để kiểm tra
            header = f.read(4)
            if header.startswith(b'<!DOCTYPE') or header.startswith(b'<html'):
                print("❌ Downloaded file is HTML, not a pickle file!")
                return False
            f.seek(0)  # Reset về đầu file
            pickle.load(f)
        return True
    except Exception as e:
        print(f"❌ Invalid pickle file: {str(e)}")
        return False

def create_model_from_csv():
    """Tạo model từ file CSV"""
    print("Creating model from CSV data...")
    
    # Đường dẫn file CSV
    csv_file = "Final result the align sentences with rescue hybrid.xlsx - aligned_with_rescue_hybrid_2.5-2.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return False
    
    try:
        # Load CSV data
        print("Loading CSV data...")
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} records from CSV")
        
        # Lấy các cột cần thiết
        han_texts = df['Câu tiếng Hán'].fillna('').astype(str).tolist()
        translations = df['translation'].fillna('').astype(str).tolist()
        best_matches = df['best_match'].fillna('').astype(str).tolist()
        
        # Tạo embeddings đơn giản với LaBSE
        print("Creating embeddings with LaBSE...")
        model = SentenceTransformer('sentence-transformers/LaBSE')
        
        # Tạo embeddings cho câu tiếng Hán (chỉ lấy 1000 câu đầu để tiết kiệm)
        max_samples = min(1000, len(han_texts))
        han_texts_subset = han_texts[:max_samples]
        han_embeddings = model.encode(han_texts_subset, convert_to_tensor=True)
        
        # Tạo vectorstore đơn giản
        vectorstore = {
            'df': df.iloc[:max_samples],  # Chỉ lấy subset
            'han_embeddings_labse': han_embeddings,
            'han_embeddings_phobert': None,  # Không dùng PhoBERT để tiết kiệm
            'labse_model': model,
            'phobert_tokenizer': None,
            'phobert_model': None,
            'device': 'cpu'
        }
        
        # Lưu model
        output_file = "han_viet_vectorstore.pkl"
        with open(output_file, 'wb') as f:
            pickle.dump(vectorstore, f)
        
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"✅ Model created successfully! File size: {file_size:.2f} MB")
        print(f"Model saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating model: {str(e)}")
        return False

def create_dummy_model():
    """Tạo model dummy để test"""
    print("Creating dummy model for testing...")
    
    # Tạo dữ liệu dummy
    dummy_data = {
        'Câu tiếng Hán': ['你好', '谢谢', '再见', '一大熱傷血', '心無血養'],
        'translation': ['Xin chào', 'Cảm ơn', 'Tạm biệt', 'Một đại nhiệt thương huyết', 'Tâm vô huyết dưỡng'],
        'best_match': ['Xin chào', 'Cảm ơn', 'Tạm biệt', 'Một đại nhiệt thương huyết', 'Tâm vô huyết dưỡng']
    }
    
    df = pd.DataFrame(dummy_data)
    
    # Tạo vector store dummy
    vectorstore = {
        'df': df,
        'han_embeddings_phobert': None,
        'han_embeddings_labse': None,
        'labse_model': None,
        'phobert_tokenizer': None,
        'phobert_model': None,
        'device': 'cpu'
    }
    
    with open('han_viet_vectorstore.pkl', 'wb') as f:
        pickle.dump(vectorstore, f)
    
    print("✅ Dummy model created successfully!")
    return True

if __name__ == "__main__":
    print("=== Model Creation Script ===")
    
    # Kiểm tra xem file đã tồn tại chưa và có hợp lệ không
    if os.path.exists("han_viet_vectorstore.pkl"):
        if validate_pickle_file("han_viet_vectorstore.pkl"):
            print("✅ Valid model file already exists!")
            exit(0)
        else:
            print("⚠️  Existing file is invalid, recreating...")
            os.remove("han_viet_vectorstore.pkl")
    
    # Thử tạo model từ CSV
    if create_model_from_csv():
        exit(0)
    
    # Nếu không được, tạo dummy model
    print("⚠️  Creating dummy model as fallback...")
    create_dummy_model() 