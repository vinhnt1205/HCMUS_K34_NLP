# -*- coding: utf-8 -*-
"""
Flask API cho hệ thống tìm kiếm Hán-Việt
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5008) 