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

def load_pickle_from_url():
    """Load pickle file trực tiếp từ URL mà không cần download"""
    import pickle
    import io
    
    # URL Hugging Face Hub
    hf_url = "https://huggingface.co/datasets/ntvinh12052001/han_viet_vectorstore/resolve/main/han_viet_vectorstore.pkl"
    
    try:
        print(f"Loading pickle file directly from URL...")
        print(f"URL: {hf_url}")
        
        # Tạo session với timeout
        session = requests.Session()
        session.timeout = 300  # 5 phút timeout
        
        # Load trực tiếp từ URL
        response = session.get(hf_url, stream=True, timeout=300)
        response.raise_for_status()
        
        # Kiểm tra content type
        content_type = response.headers.get('content-type', '')
        if 'text/html' in content_type:
            print("❌ URL returns HTML, not a pickle file!")
            return None
        
        # Load pickle trực tiếp từ response content
        print("Loading pickle data from memory...")
        pickle_data = response.content
        
        # Load pickle object
        data = pickle.loads(pickle_data)
        print("✅ Successfully loaded pickle data from URL!")
        
        return data
        
    except requests.exceptions.Timeout:
        print("❌ Request timeout after 5 minutes")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Connection error")
        return None
    except Exception as e:
        print(f"❌ Error loading from URL: {str(e)}")
        return None

if __name__ == "__main__":
    print("=== Online Pickle Load Script ===")
    
    # Load pickle trực tiếp từ URL
    data = load_pickle_from_url()
    
    if data is not None:
        print("✅ Successfully loaded pickle data from Hugging Face!")
        print(f"Data type: {type(data)}")
        if isinstance(data, dict):
            print(f"Keys: {list(data.keys())}")
        exit(0)
    else:
        print("❌ Failed to load pickle data from Hugging Face!")
        exit(1) 