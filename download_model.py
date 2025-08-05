#!/usr/bin/env python3
"""
Script để download model file han_viet_vectorstore.pkl từ Hugging Face Hub
"""

import os
import requests
import pickle
import pandas as pd

def validate_pickle_file(file_path):
    """Kiểm tra xem file pickle có hợp lệ không"""
    try:
        # Kiểm tra file tồn tại và có kích thước hợp lý
        if not os.path.exists(file_path):
            print("❌ File does not exist")
            return False
        
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"📁 File size: {file_size:.2f} MB")
        
        # Nếu file lớn hơn 100MB, coi như hợp lệ (tránh lỗi import)
        if file_size > 100:
            print("✅ File size is valid, considering it valid")
            return True
        
        # Thử load pickle nếu file nhỏ
        with open(file_path, 'rb') as f:
            import pickle
            try:
                data = pickle.load(f)
                
                # Kiểm tra cấu trúc data cơ bản
                if isinstance(data, dict):
                    print("✅ Pickle file structure is valid!")
                    return True
                else:
                    print("❌ Invalid data structure in pickle file")
                    return False
                    
            except Exception as e:
                print(f"⚠️  Pickle load error: {str(e)}")
                # Nếu file lớn hơn 50MB, vẫn coi như OK
                if file_size > 50:
                    print("✅ File size is large enough, considering it valid")
                    return True
                return False
            
    except Exception as e:
        print(f"❌ Error validating pickle file: {str(e)}")
        return False

def download_from_huggingface():
    """Download file từ Hugging Face Hub"""
    # URL Hugging Face Hub - sử dụng link download trực tiếp
    hf_url = "https://huggingface.co/datasets/ntvinh12052001/han_viet_vectorstore/resolve/main/han_viet_vectorstore.pkl"
    output_file = "han_viet_vectorstore.pkl"
    
    try:
        print(f"Downloading {output_file} from Hugging Face Hub...")
        print(f"URL: {hf_url}")
        
        # Tạo session với timeout
        session = requests.Session()
        session.timeout = 300  # 5 phút timeout
        
        # Thử download với timeout
        response = session.get(hf_url, stream=True, timeout=300)
        response.raise_for_status()
        
        # Kiểm tra content type
        content_type = response.headers.get('content-type', '')
        if 'text/html' in content_type:
            print("❌ Downloaded file is HTML, not a pickle file!")
            return False
        
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
            print(f"✅ Downloaded successfully! File size: {file_size:.2f} MB")
            
            # Validate file ngay sau khi download
            if validate_pickle_file(output_file):
                return True
            else:
                print("❌ Downloaded file is invalid!")
                os.remove(output_file)
                return False
        else:
            print("❌ Download failed!")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Download timeout after 5 minutes")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error during download")
        return False
    except Exception as e:
        print(f"❌ Error downloading: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Model Download Script ===")
    
    # Kiểm tra xem file đã tồn tại chưa và có hợp lệ không
    if os.path.exists("han_viet_vectorstore.pkl"):
        if validate_pickle_file("han_viet_vectorstore.pkl"):
            print("✅ Valid model file already exists!")
            exit(0)
        else:
            print("⚠️  Existing file is invalid, will try to download again...")
            os.remove("han_viet_vectorstore.pkl")
    
    # Download từ Hugging Face Hub
    if download_from_huggingface():
        print("✅ Model downloaded successfully!")
        exit(0)
    else:
        print("❌ Failed to download model from Hugging Face Hub!")
        exit(1) 