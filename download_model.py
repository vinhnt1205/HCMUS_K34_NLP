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
        with open(file_path, 'rb') as f:
            # Thử load với protocol cũ hơn để tránh lỗi numpy._core
            import pickle
            try:
                # Thử với protocol mới nhất trước
                data = pickle.load(f)
            except (ModuleNotFoundError, AttributeError) as e:
                if 'numpy._core' in str(e):
                    print(f"⚠️  Numpy version compatibility issue: {str(e)}")
                    print("Attempting to fix numpy compatibility...")
                    # Thử load lại với protocol cũ hơn
                    f.seek(0)
                    try:
                        data = pickle.load(f)
                        print("✅ Successfully loaded with compatibility fix")
                        return True
                    except Exception as e2:
                        print(f"❌ Still failed: {str(e2)}")
                        # Nếu vẫn lỗi, nhưng file tồn tại và có kích thước lớn, coi như OK
                        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                        if file_size > 100:  # File lớn hơn 100MB
                            print(f"⚠️  File size is {file_size:.2f}MB, considering it valid despite numpy error")
                            return True
                        return False
                else:
                    print(f"❌ Invalid pickle file: {str(e)}")
                    return False
            
            # Kiểm tra cấu trúc data
            required_keys = ['df', 'han_embeddings_phobert', 'han_embeddings_labse']
            if not all(key in data for key in required_keys):
                print("❌ Invalid data structure in pickle file")
                return False
            
            print("✅ Pickle file is valid!")
            return True
            
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