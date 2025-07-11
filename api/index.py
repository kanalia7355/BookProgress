from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
import json
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# OpenBD API クラスを直接定義
class OpenBDApi:
    def __init__(self):
        self.base_url = "https://api.openbd.jp/v1/get"
    
    def get_book_by_isbn(self, isbn):
        cleaned_isbn = self.clean_isbn(isbn)
        print(f"Searching for ISBN: {cleaned_isbn}")
        
        book_data = self.get_from_openbd(cleaned_isbn)
        return book_data
    
    def clean_isbn(self, isbn):
        # ISBNから数字とXのみを抽出
        cleaned = re.sub(r'[^0-9X]', '', isbn.upper())
        print(f"Cleaned ISBN: {cleaned}")
        return cleaned
    
    def get_from_openbd(self, isbn):
        try:
            # OpenBD APIに複数のISBNを送信可能（カンマ区切り）
            response = requests.get(f"{self.base_url}?isbn={isbn}", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            print(f"OpenBD API response length: {len(data) if data else 0}")
            
            if data and len(data) > 0 and data[0] is not None:
                book_info = data[0]
                print(f"Book info keys: {list(book_info.keys())}")
                
                # summaryオブジェクトから基本情報を取得
                summary = book_info.get('summary', {})
                print(f"Summary: {summary}")
                
                # onixオブジェクトから詳細情報を取得
                onix = book_info.get('onix', {})
                print(f"Onix keys: {list(onix.keys()) if onix else 'None'}")
                
                # タイトルの取得（複数の方法を試行）
                title = self.extract_title(onix, summary)
                
                # 著者情報の取得
                author = self.extract_author(onix, summary)
                
                # 出版社の取得
                publisher = self.extract_publisher(onix, summary)
                
                # ページ数の取得
                total_pages = self.extract_pages(onix, summary)
                
                # 出版日の取得
                pubdate = self.extract_pubdate(onix, summary)
                
                # 表紙画像の取得
                cover_image = self.extract_cover_image(onix, summary)
                
                result = {
                    'isbn': isbn,
                    'title': title,
                    'author': author,
                    'publisher': publisher,
                    'pubdate': pubdate,
                    'totalPages': total_pages,
                    'coverImage': cover_image,
                    'currentPage': 0,
                    'readingTime': 0
                }
                
                print(f"Final result: {result}")
                return result
            else:
                print("No book data found in OpenBD response")
                return None
                
        except requests.RequestException as e:
            print(f"OpenBD API request error: {e}")
            return None
        except Exception as e:
            print(f"OpenBD API error: {e}")
            return None
    
    def extract_title(self, onix, summary):
        # summaryから取得
        title = summary.get('title', '')
        if title:
            return title
        
        # onixから取得
        try:
            title_detail = onix.get('DescriptiveDetail', {}).get('TitleDetail', {})
            if isinstance(title_detail, dict):
                title_element = title_detail.get('TitleElement', {})
                if isinstance(title_element, dict):
                    title_text = title_element.get('TitleText', {})
                    if isinstance(title_text, dict):
                        return title_text.get('content', '')
        except Exception as e:
            print(f"Error extracting title: {e}")
        
        return ''
    
    def extract_publisher(self, onix, summary):
        # summaryから取得
        publisher = summary.get('publisher', '')
        if publisher:
            return publisher
        
        # onixから取得
        try:
            publishing_detail = onix.get('PublishingDetail', {})
            if isinstance(publishing_detail, dict):
                publishers = publishing_detail.get('Publisher', [])
                if isinstance(publishers, list) and len(publishers) > 0:
                    publisher_name = publishers[0].get('PublisherName', '')
                    if publisher_name:
                        return publisher_name
        except Exception as e:
            print(f"Error extracting publisher: {e}")
        
        return ''
    
    def extract_author(self, onix, summary):
        # summaryから著者情報を取得
        author = summary.get('author', '')
        if author:
            return author
        
        # onixから著者情報を取得
        try:
            contributors = onix.get('DescriptiveDetail', {}).get('Contributor', [])
            if isinstance(contributors, list) and len(contributors) > 0:
                for contributor in contributors:
                    # ContributorRoleが配列の場合とstrの場合を考慮
                    contributor_roles = contributor.get('ContributorRole', [])
                    if isinstance(contributor_roles, list):
                        if 'A01' in contributor_roles:  # 著者
                            person_name = contributor.get('PersonName', {})
                            if isinstance(person_name, dict):
                                return person_name.get('content', '')
                            elif isinstance(person_name, str):
                                return person_name
                    elif contributor_roles == 'A01':
                        person_name = contributor.get('PersonName', {})
                        if isinstance(person_name, dict):
                            return person_name.get('content', '')
                        elif isinstance(person_name, str):
                            return person_name
                
                # 最初の著者を取得（役割が不明な場合）
                if len(contributors) > 0:
                    person_name = contributors[0].get('PersonName', {})
                    if isinstance(person_name, dict):
                        return person_name.get('content', '')
                    elif isinstance(person_name, str):
                        return person_name
                        
        except Exception as e:
            print(f"Error extracting author: {e}")
        
        return ''
    
    def extract_pages(self, onix, summary):
        # summaryから取得を試行
        extent = summary.get('extent', '')
        if extent:
            pages = self.parse_pages_from_text(extent)
            if pages > 0:
                return pages
        
        # onixから取得を試行
        try:
            extents = onix.get('DescriptiveDetail', {}).get('Extent', [])
            if isinstance(extents, list):
                for extent in extents:
                    if extent.get('ExtentType') == '00':  # ページ数
                        extent_value = extent.get('ExtentValue', '')
                        if extent_value and extent_value.isdigit():
                            return int(extent_value)
        except Exception as e:
            print(f"Error extracting pages: {e}")
        
        return 0
    
    def extract_pubdate(self, onix, summary):
        # summaryから取得
        pubdate = summary.get('pubdate', '')
        if pubdate:
            return pubdate
        
        # onixから取得
        try:
            pub_dates = onix.get('PublishingDetail', {}).get('PublishingDate', [])
            if isinstance(pub_dates, list):
                for pub_date in pub_dates:
                    if pub_date.get('PublishingDateRole') == '01':  # 出版日
                        date_format = pub_date.get('DateFormat', '')
                        date_value = pub_date.get('Date', '')
                        if date_value:
                            return date_value
        except Exception as e:
            print(f"Error extracting pubdate: {e}")
        
        return ''
    
    def extract_cover_image(self, onix, summary):
        # summaryから取得
        cover = summary.get('cover', '')
        if cover:
            return cover
        
        # onixから取得
        try:
            collateral_detail = onix.get('CollateralDetail', {})
            supporting_resources = collateral_detail.get('SupportingResource', [])
            if isinstance(supporting_resources, list):
                for resource in supporting_resources:
                    if resource.get('ResourceContentType') == '01':  # 表紙画像
                        versions = resource.get('ResourceVersion', [])
                        if isinstance(versions, list):
                            for version in versions:
                                links = version.get('ResourceLink', [])
                                if isinstance(links, list) and len(links) > 0:
                                    return links[0]
        except Exception as e:
            print(f"Error extracting cover image: {e}")
        
        return ''
    
    def parse_pages_from_text(self, text):
        if not text:
            return 0
        
        # 「123p」「123ページ」「123頁」などの形式を検索
        patterns = [
            r'(\d+)p\b',
            r'(\d+)ページ',
            r'(\d+)頁',
            r'(\d+)\s*p\b',
            r'(\d+)\s*pages?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # 数字のみの場合
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        return 0
    

# BookService クラスを直接定義
class BookService:
    def __init__(self):
        self.books = []
    
    def get_all_books(self):
        return self.books
    
    def save_book(self, book_data):
        if 'id' not in book_data:
            book_data['id'] = self.generate_id()
        
        book_data['created_at'] = datetime.now().isoformat()
        book_data['updated_at'] = datetime.now().isoformat()
        
        self.books.append(book_data)
        return book_data
    
    def update_book(self, book_id, book_data):
        for i, book in enumerate(self.books):
            if book.get('id') == book_id:
                book_data['updated_at'] = datetime.now().isoformat()
                self.books[i] = {**book, **book_data}
                return self.books[i]
        return None
    
    def delete_book(self, book_id):
        original_length = len(self.books)
        self.books = [book for book in self.books if book.get('id') != book_id]
        return len(self.books) < original_length
    
    def generate_id(self):
        import time
        import random
        return f"{int(time.time())}{random.randint(1000, 9999)}"

openbd_api = OpenBDApi()
book_service = BookService()

@app.route('/api/book/<isbn>', methods=['GET'])
def get_book_by_isbn(isbn):
    try:
        print(f"=== Received ISBN request: {isbn} ===")
        
        # ISBNのバリデーション
        if not isbn or len(isbn) < 10:
            return jsonify({'error': 'ISBNが無効です'}), 400
        
        # 書籍データを取得
        book_data = openbd_api.get_book_by_isbn(isbn)
        
        if book_data:
            print(f"=== Book data found: {book_data} ===")
            return jsonify(book_data)
        else:
            print("=== No book data found ===")
            return jsonify({
                'error': '書籍が見つかりません', 
                'isbn': isbn,
                'message': 'OpenBD APIでこのISBNの書籍情報を見つけることができませんでした'
            }), 404
            
    except Exception as e:
        print(f"=== Error in get_book_by_isbn: {e} ===")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'isbn': isbn,
            'message': 'サーバーエラーが発生しました'
        }), 500

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

@app.route('/api/test-openbd/<isbn>', methods=['GET'])
def test_openbd(isbn):
    """OpenBD APIの動作をテストするエンドポイント"""
    try:
        print(f"Testing OpenBD API with ISBN: {isbn}")
        
        # 直接OpenBD APIを呼び出し
        import requests
        response = requests.get(f"https://api.openbd.jp/v1/get?isbn={isbn}", timeout=10)
        
        return jsonify({
            'status_code': response.status_code,
            'response_data': response.json(),
            'isbn': isbn
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'isbn': isbn
        }), 500

# Vercel用のメインハンドラー
app_handler = app

# Vercel用のエントリーポイント
def handler(request, context):
    return app_handler

# デフォルトエクスポート
if __name__ == "__main__":
    app.run(debug=True)