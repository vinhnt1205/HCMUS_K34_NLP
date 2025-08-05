# -*- coding: utf-8 -*-
"""
Flask API cho hệ thống tìm kiếm Hán-Việt - Lightweight version
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys
import gc

# Thêm current directory vào Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)

# Global variable để cache model
model_loaded = False
vectorstore = None

def load_model_lazy():
    """Load model chỉ khi cần thiết"""
    global model_loaded, vectorstore
    
    if not model_loaded:
        try:
            print("Loading model on first request...")
            from han_viet_search_system import load_vectorstore
            vectorstore = load_vectorstore()
            model_loaded = True
            print("✅ Model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            return False
    return True

def search_simple(query_han):
    """Simple search function để tiết kiệm memory"""
    try:
        if not load_model_lazy():
            return None
            
        # Simple search logic
        results = []
        df = vectorstore['df']
        
        # Tìm kiếm đơn giản
        for idx, row in df.iterrows():
            if query_han in str(row['Câu tiếng Hán']):
                results.append({
                    'score': 0.8,
                    'model': 'simple',
                    'han_original': row['Câu tiếng Hán'],
                    'translation': row['translation'],
                    'best_match': row['best_match']
                })
                break
        
        # Nếu không tìm thấy, trả về kết quả mặc định
        if not results:
            results.append({
                'score': 0.5,
                'model': 'simple',
                'han_original': query_han,
                'translation': 'Không tìm thấy bản dịch',
                'best_match': 'Không tìm thấy bản dịch'
            })
        
        return results
        
    except Exception as e:
        print(f"Error in search: {str(e)}")
        return None

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
        
        # Tìm kiếm với simple search
        results = search_simple(query_han)
        
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
        # Tạo dummy model nhẹ
        import pandas as pd
        import pickle
        
        dummy_data = {
            'Câu tiếng Hán': ['你好', '谢谢', '再见'],
            'translation': ['Xin chào', 'Cảm ơn', 'Tạm biệt'],
            'best_match': ['Xin chào', 'Cảm ơn', 'Tạm biệt']
        }
        
        df = pd.DataFrame(dummy_data)
        vectorstore = {'df': df}
        
        with open('han_viet_vectorstore.pkl', 'wb') as f:
            pickle.dump(vectorstore, f)
        
        return jsonify({'status': 'success', 'message': 'Lightweight model created'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5008))
    app.run(debug=False, host='0.0.0.0', port=port) 