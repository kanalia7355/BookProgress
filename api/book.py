from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# OpenBD API クラス
class OpenBDApi:
    def __init__(self):
        self.base_url = "https://api.openbd.jp/v1/get"
    
    def get_book_by_isbn(self, isbn):
        cleaned_isbn = self.clean_isbn(isbn)
        print(f"Searching for ISBN: {cleaned_isbn}")
        
        book_data = self.get_from_openbd(cleaned_isbn)
        return book_data
    
    def clean_isbn(self, isbn):
        cleaned = re.sub(r'[^0-9X]', '', isbn.upper())
        print(f"Cleaned ISBN: {cleaned}")
        return cleaned
    
    def get_from_openbd(self, isbn):
        try:
            response = requests.get(f"{self.base_url}?isbn={isbn}", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            print(f"OpenBD API response length: {len(data) if data else 0}")
            
            if data and len(data) > 0 and data[0] is not None:
                book_info = data[0]
                
                summary = book_info.get('summary', {})
                onix = book_info.get('onix', {})
                
                title = self.extract_title(onix, summary)
                author = self.extract_author(onix, summary)
                publisher = self.extract_publisher(onix, summary)
                total_pages = self.extract_pages(onix, summary)
                pubdate = self.extract_pubdate(onix, summary)
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
                
        except Exception as e:
            print(f"OpenBD API error: {e}")
            return None
    
    def extract_title(self, onix, summary):
        title = summary.get('title', '')
        if title:
            return title
        
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
    
    def extract_author(self, onix, summary):
        author = summary.get('author', '')
        if author:
            return author
        
        try:
            contributors = onix.get('DescriptiveDetail', {}).get('Contributor', [])
            if isinstance(contributors, list) and len(contributors) > 0:
                for contributor in contributors:
                    person_name = contributor.get('PersonName', {})
                    if isinstance(person_name, dict):
                        return person_name.get('content', '')
                    elif isinstance(person_name, str):
                        return person_name
        except Exception as e:
            print(f"Error extracting author: {e}")
        
        return ''
    
    def extract_publisher(self, onix, summary):
        return summary.get('publisher', '')
    
    def extract_pages(self, onix, summary):
        extent = summary.get('extent', '')
        if extent:
            return self.parse_pages_from_text(extent)
        return 0
    
    def extract_pubdate(self, onix, summary):
        return summary.get('pubdate', '')
    
    def extract_cover_image(self, onix, summary):
        return summary.get('cover', '')
    
    def parse_pages_from_text(self, text):
        if not text:
            return 0
        
        patterns = [r'(\d+)p\b', r'(\d+)ページ', r'(\d+)頁']
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        return 0

# API インスタンス
openbd_api = OpenBDApi()

@app.route('/api/book/<isbn>', methods=['GET'])
def get_book_by_isbn(isbn):
    try:
        print(f"=== Book API request for ISBN: {isbn} ===")
        
        if not isbn or len(isbn) < 10:
            return jsonify({'error': 'ISBNが無効です'}), 400
        
        book_data = openbd_api.get_book_by_isbn(isbn)
        
        if book_data:
            print(f"=== Book data found ===")
            return jsonify(book_data)
        else:
            print("=== No book data found ===")
            return jsonify({
                'error': '書籍が見つかりません', 
                'isbn': isbn
            }), 404
            
    except Exception as e:
        print(f"=== Error: {e} ===")
        return jsonify({
            'error': str(e),
            'isbn': isbn
        }), 500

# Vercel用のハンドラー
def handler(request, context):
    return app

if __name__ == "__main__":
    app.run(debug=True)