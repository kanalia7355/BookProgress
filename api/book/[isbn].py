from flask import Flask, jsonify
import json
import requests
import re

app = Flask(__name__)

def get_book_by_isbn(isbn):
    """OpenBD APIから書籍情報を取得"""
    try:
        # ISBNをクリーニング
        cleaned_isbn = re.sub(r'[^0-9X]', '', isbn.upper())
        
        # OpenBD APIを呼び出し
        response = requests.get(f"https://api.openbd.jp/v1/get?isbn={cleaned_isbn}", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data and len(data) > 0 and data[0] is not None:
            book_info = data[0]
            summary = book_info.get('summary', {})
            onix = book_info.get('onix', {})
            
            # タイトル取得
            title = summary.get('title', '')
            if not title and onix:
                try:
                    title_detail = onix.get('DescriptiveDetail', {}).get('TitleDetail', {})
                    title_element = title_detail.get('TitleElement', {})
                    title_text = title_element.get('TitleText', {})
                    title = title_text.get('content', '')
                except:
                    pass
            
            # 著者取得
            author = summary.get('author', '')
            if not author and onix:
                try:
                    contributors = onix.get('DescriptiveDetail', {}).get('Contributor', [])
                    if isinstance(contributors, list) and len(contributors) > 0:
                        person_name = contributors[0].get('PersonName', {})
                        if isinstance(person_name, dict):
                            author = person_name.get('content', '')
                        elif isinstance(person_name, str):
                            author = person_name
                except:
                    pass
            
            # ページ数取得
            pages = 0
            extent = summary.get('extent', '')
            if extent:
                page_match = re.search(r'(\d+)[pページ頁]', extent)
                if page_match:
                    pages = int(page_match.group(1))
            
            return {
                'isbn': isbn,
                'title': title,
                'author': author,
                'publisher': summary.get('publisher', ''),
                'pubdate': summary.get('pubdate', ''),
                'totalPages': pages,
                'coverImage': summary.get('cover', ''),
                'currentPage': 0,
                'readingTime': 0
            }
        
        return None
        
    except Exception as e:
        print(f"Error fetching book data: {e}")
        return None

def handler(request):
    """Vercel用のハンドラー"""
    if request.method == 'GET':
        # URLパスからISBNを取得
        path = request.path
        isbn = path.split('/')[-1]
        
        if not isbn or len(isbn) < 10:
            return jsonify({'error': 'ISBNが無効です'}), 400
        
        book_data = get_book_by_isbn(isbn)
        
        if book_data:
            return jsonify(book_data)
        else:
            return jsonify({
                'error': '書籍が見つかりません',
                'isbn': isbn
            }), 404
    
    return jsonify({'error': 'Method not allowed'}), 405