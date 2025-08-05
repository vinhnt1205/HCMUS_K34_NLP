# -*- coding: utf-8 -*-
"""
Flask API cho hệ thống tìm kiếm Hán-Việt
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys

# Thêm current directory vào Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import sau khi đã setup path
from han_viet_search_system import HanVietVectorStore

app = Flask(__name__)
CORS(app)

# Biến global để lưu trữ vectorstore instance
vectorstore_instance = None

def initialize_vectorstore():
    """Khởi tạo vectorstore một lần duy nhất"""
    global vectorstore_instance
    
    if vectorstore_instance is not None:
        return vectorstore_instance
    
    print("=== Initializing Han-Viet Search System ===")
    try:
        model_path = "han_viet_vectorstore.pkl"
        if not os.path.exists(model_path):
            print("Model file not found, loading from Hugging Face Hub...")
            import download_model
            data = download_model.load_pickle_from_url()
            if data is None:
                print("❌ Load failed! Model file is required.")
                return None
        else:
            print("Model file exists, validating...")
            import download_model
            if not download_model.validate_pickle_file(model_path):
                            print("Invalid model file, loading from URL...")
            os.remove(model_path)
            data = download_model.load_pickle_from_url()
            if data is None:
                print("❌ Load failed! Model file is required.")
                return None
        
        # Load vectorstore một lần duy nhất với memory optimization
        print("Loading vectorstore with memory optimization...")
        import gc
        gc.collect()  # Clean up memory before loading
        
        vectorstore_instance = HanVietVectorStore(None)
        # Load trực tiếp từ Hugging Face URL
        vectorstore_instance.load_vectorstore("https://huggingface.co/datasets/ntvinh12052001/han_viet_vectorstore/resolve/main/han_viet_vectorstore.pkl")
        
        # Clean up memory after loading
        gc.collect()
        print("✅ Vectorstore loaded successfully!")
        
        return vectorstore_instance
        
    except Exception as e:
        print(f"❌ Error during vectorstore initialization: {str(e)}")
        print("Will try to download model on first request...")
        return None

# Khởi tạo vectorstore khi app start
vectorstore_instance = initialize_vectorstore()

@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    """API endpoint để tìm kiếm"""
    global vectorstore_instance
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dữ liệu không hợp lệ'
            }), 400
            
        query_han = data.get('query', '').strip()
        
        if not query_han:
            return jsonify({
                'success': False,
                'error': 'Vui lòng nhập câu tiếng Hán'
            }), 400
        
        # Kiểm tra xem vectorstore đã được load chưa
        if vectorstore_instance is None:
            print("Vectorstore not initialized, trying to initialize...")
            vectorstore_instance = initialize_vectorstore()
            if vectorstore_instance is None:
                return jsonify({
                    'success': False,
                    'error': 'Hệ thống chưa sẵn sàng, vui lòng thử lại sau'
                }), 503
        
        # Tìm kiếm sử dụng instance đã load sẵn
        results = vectorstore_instance.search(query_han)
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy kết quả phù hợp'
            }), 404
        
        # Format kết quả
        formatted_results = []
        for result in results:
            formatted_results.append({
                'score': round(result['score'], 4),
                'model': result['model'],
                'han_original': result['han_original'],
                'translation': result['translation'],
                'best_match': result['best_match']
            })
        
        return jsonify({
            'success': True,
            'query': query_han,
            'results': formatted_results,
            'best_result': formatted_results[0] if formatted_results else None
        })
        
    except Exception as e:
        print(f"Error in search API: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Lỗi: {str(e)}'
        }), 500

@app.route('/api/health')
def health():
    """Health check"""
    global vectorstore_instance
    status = 'healthy' if vectorstore_instance is not None else 'initializing'
    return jsonify({
        'status': status,
        'vectorstore_loaded': vectorstore_instance is not None
    })

@app.route('/api/init-model')
def init_model():
    """Khởi tạo model nếu chưa có"""
    global vectorstore_instance
    
    try:
        if vectorstore_instance is not None:
            return jsonify({'status': 'success', 'message': 'Vectorstore already loaded'})
        
        vectorstore_instance = initialize_vectorstore()
        if vectorstore_instance is not None:
            return jsonify({'status': 'success', 'message': 'Vectorstore loaded successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to load vectorstore'}), 500
            
    except Exception as e:
        print(f"Unexpected error in init_model: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Failed to initialize model: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5008))
    # Tối ưu hóa cho production
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True) 