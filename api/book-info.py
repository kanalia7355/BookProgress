from http.server import BaseHTTPRequestHandler
import json
import requests
import re
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # URLパースしてISBNを取得
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        isbn = query_params.get('isbn', [None])[0]
        
        if not isbn:
            self.send_error_response(400, 'ISBNパラメータが必要です')
            return
        
        if len(isbn) < 10:
            self.send_error_response(400, 'ISBNが無効です')
            return
        
        try:
            book_data = self.get_book_by_isbn(isbn)
            
            if book_data:
                self.send_json_response(book_data)
            else:
                self.send_error_response(404, '書籍が見つかりません')
                
        except Exception as e:
            self.send_error_response(500, f'サーバーエラー: {str(e)}')
    
    def get_book_by_isbn(self, isbn):
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
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def send_error_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_data = {'error': message}
        self.wfile.write(json.dumps(error_data, ensure_ascii=False).encode('utf-8'))