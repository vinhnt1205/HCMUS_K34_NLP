#!/usr/bin/env python3
"""
Script để download model file han_viet_vectorstore.pkl
"""

import os
import requests
from pathlib import Path

def download_from_google_drive():
    """Download file từ Google Drive"""
    # URL Google Drive (bạn cần thay đổi URL này)
    # Cách lấy URL: Upload file lên Google Drive, share với "Anyone with the link"
    # Sau đó copy URL và thay thế /view?usp=sharing bằng /uc?export=download
    gdrive_url = "https://drive.google.com/uc?export=download&id=1C4jgr69xIQqpiuwcPFdk34jAvp61gtjK"
    
    output_file = "han_viet_vectorstore.pkl"
    
    try:
        print(f"Downloading {output_file} from Google Drive...")
        print(f"URL: {gdrive_url}")
        
        # Download trực tiếp từ Google Drive
        return download_direct_from_gdrive(gdrive_url, output_file)
            
    except Exception as e:
        print(f"❌ Error downloading: {str(e)}")
        return False

def download_direct_from_gdrive(gdrive_url, output_file):
    """Download trực tiếp từ Google Drive"""
    try:
        # Tạo session để handle redirects
        session = requests.Session()
        response = session.get(gdrive_url, stream=True)
        response.raise_for_status()
        
        # Kiểm tra nếu file quá lớn (Google Drive warning)
        if 'drive.google.com' in response.url and 'confirm=' in response.url:
            # Cần confirm download
            confirm_token = response.url.split('confirm=')[1].split('&')[0]
            confirm_url = f"{gdrive_url}&confirm={confirm_token}"
            response = session.get(confirm_url, stream=True)
            response.raise_for_status()
        
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
            print(f"✅ Direct download successful! File size: {file_size:.2f} MB")
            return True
        else:
            print("❌ Direct download failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error in direct download: {str(e)}")
        return False

def download_from_direct_url():
    """Download file từ direct URL"""
    # Bạn có thể upload file lên các dịch vụ như:
    # - https://file.io/ (temporary)
    # - https://transfer.sh/ (temporary)
    # - https://anonfiles.com/ (permanent)
    direct_url = "YOUR_DIRECT_URL_HERE"
    
    output_file = "han_viet_vectorstore.pkl"
    
    try:
        print(f"Downloading {output_file} from direct URL...")
        response = requests.get(direct_url, stream=True)
        response.raise_for_status()
        
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"✅ Downloaded successfully! File size: {file_size:.2f} MB")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading: {str(e)}")
        return False

def create_dummy_model():
    """Tạo model dummy để test (chỉ dùng cho development)"""
    import pickle
    import pandas as pd
    
    print("Creating dummy model for testing...")
    
    # Tạo dữ liệu dummy
    dummy_data = {
        'han_original': ['你好', '谢谢', '再见'],
        'translation': ['Xin chào', 'Cảm ơn', 'Tạm biệt'],
        'best_match': ['Xin chào', 'Cảm ơn', 'Tạm biệt']
    }
    
    df = pd.DataFrame(dummy_data)
    
    # Tạo vector store dummy
    vectorstore = {
        'df': df,
        'han_embeddings_phobert': None,
        'han_embeddings_labse': None
    }
    
    with open('han_viet_vectorstore.pkl', 'wb') as f:
        pickle.dump(vectorstore, f)
    
    print("✅ Dummy model created successfully!")
    return True

if __name__ == "__main__":
    print("=== Model Download Script ===")
    
    # Kiểm tra xem file đã tồn tại chưa
    if os.path.exists("han_viet_vectorstore.pkl"):
        print("✅ Model file already exists!")
        exit(0)
    
    # Thử download từ Google Drive trước
    if download_from_google_drive():
        exit(0)
    
    # Nếu không được, thử direct URL
    if download_from_direct_url():
        exit(0)
    
    # Nếu không có URL nào, tạo dummy model
    print("⚠️  No download URLs configured. Creating dummy model for testing...")
    create_dummy_model() 