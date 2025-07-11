from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# パッケージのパスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api.ndl_api import NDLApi
from backend.api.book_service import BookService

app = Flask(__name__)
CORS(app)

ndl_api = NDLApi()
book_service = BookService(data_file='data/books.json')

@app.route('/api/book/<isbn>', methods=['GET'])
def get_book_by_isbn(isbn):
    try:
        book_data = ndl_api.get_book_by_isbn(isbn)
        if book_data:
            return jsonify(book_data)
        else:
            return jsonify({'error': '書籍が見つかりません'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books', methods=['GET'])
def get_all_books():
    try:
        books = book_service.get_all_books()
        return jsonify(books)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books', methods=['POST'])
def save_book():
    try:
        book_data = request.get_json()
        saved_book = book_service.save_book(book_data)
        return jsonify(saved_book), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        book_data = request.get_json()
        updated_book = book_service.update_book(book_id, book_data)
        if updated_book:
            return jsonify(updated_book)
        else:
            return jsonify({'error': '書籍が見つかりません'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        success = book_service.delete_book(book_id)
        if success:
            return jsonify({'message': '書籍が削除されました'})
        else:
            return jsonify({'error': '書籍が見つかりません'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

# Vercel用のハンドラー
def handler(request):
    return app(request.environ, lambda status, headers: None)