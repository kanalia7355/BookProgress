import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
import re

class NDLApi:
    def __init__(self):
        self.base_url = "https://iss.ndl.go.jp/api/sru"
        self.openbd_url = "https://api.openbd.jp/v1/get"
    
    def get_book_by_isbn(self, isbn):
        cleaned_isbn = self.clean_isbn(isbn)
        
        book_data = self.get_from_openbd(cleaned_isbn)
        if book_data:
            return book_data
        
        book_data = self.get_from_ndl(cleaned_isbn)
        return book_data
    
    def clean_isbn(self, isbn):
        return re.sub(r'[^0-9X]', '', isbn.upper())
    
    def get_from_openbd(self, isbn):
        try:
            response = requests.get(f"{self.openbd_url}?isbn={isbn}")
            response.raise_for_status()
            
            data = response.json()
            if data and data[0]:
                book_info = data[0]
                summary = book_info.get('summary', {})
                
                return {
                    'isbn': isbn,
                    'title': summary.get('title', ''),
                    'author': summary.get('author', ''),
                    'publisher': summary.get('publisher', ''),
                    'pubdate': summary.get('pubdate', ''),
                    'totalPages': self.extract_pages(summary.get('extent', '')),
                    'coverImage': summary.get('cover', ''),
                    'currentPage': 0,
                    'readingTime': 0
                }
        except Exception as e:
            print(f"OpenBD API error: {e}")
            return None
    
    def get_from_ndl(self, isbn):
        try:
            query = f'isbn="{isbn}"'
            params = {
                'operation': 'searchRetrieve',
                'version': '1.2',
                'query': query,
                'recordSchema': 'dcndl',
                'maximumRecords': '1'
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            ns = {
                'srw': 'http://www.loc.gov/zing/srw/',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'dcndl': 'http://ndl.go.jp/dcndl/terms/',
                'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'
            }
            
            records = root.findall('.//srw:record', ns)
            if not records:
                return None
            
            record = records[0]
            
            title_elem = record.find('.//dc:title', ns)
            title = title_elem.text if title_elem is not None else ''
            
            author_elem = record.find('.//dc:creator', ns)
            author = author_elem.text if author_elem is not None else ''
            
            publisher_elem = record.find('.//dc:publisher', ns)
            publisher = publisher_elem.text if publisher_elem is not None else ''
            
            date_elem = record.find('.//dc:date', ns)
            pubdate = date_elem.text if date_elem is not None else ''
            
            extent_elem = record.find('.//dcndl:extent', ns)
            extent = extent_elem.text if extent_elem is not None else ''
            
            return {
                'isbn': isbn,
                'title': title,
                'author': author,
                'publisher': publisher,
                'pubdate': pubdate,
                'totalPages': self.extract_pages(extent),
                'coverImage': '',
                'currentPage': 0,
                'readingTime': 0
            }
            
        except Exception as e:
            print(f"NDL API error: {e}")
            return None
    
    def extract_pages(self, extent_text):
        if not extent_text:
            return 0
        
        page_pattern = r'(\d+)p'
        match = re.search(page_pattern, extent_text)
        if match:
            return int(match.group(1))
        
        number_pattern = r'(\d+)'
        match = re.search(number_pattern, extent_text)
        if match:
            return int(match.group(1))
        
        return 0