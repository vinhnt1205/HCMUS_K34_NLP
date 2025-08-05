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
from han_viet_search_system import load_and_search

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    """API endpoint để tìm kiếm"""
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
        
        # Tìm kiếm
        results = load_and_search(query_han)
        
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
    return jsonify({'status': 'healthy'})

@app.route('/api/init-model')
def init_model():
    """Khởi tạo model nếu chưa có"""
    try:
        model_path = "han_viet_vectorstore.pkl"
        if not os.path.exists(model_path):
            print("Model file not found, attempting to download...")
            try:
                import download_model
                success = download_model.download_from_google_drive()
                if success:
                    return jsonify({'status': 'success', 'message': 'Model downloaded successfully'})
                else:
                    # Tạo dummy model
                    download_model.create_dummy_model()
                    return jsonify({'status': 'warning', 'message': 'Using dummy model'})
            except Exception as e:
                print(f"Error downloading model: {str(e)}")
                # Tạo dummy model
                import download_model
                download_model.create_dummy_model()
                return jsonify({'status': 'warning', 'message': f'Using dummy model due to error: {str(e)}'})
        else:
            return jsonify({'status': 'success', 'message': 'Model already exists'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5008))
    app.run(debug=False, host='0.0.0.0', port=port) 