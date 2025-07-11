import json
import os
from datetime import datetime

class BookService:
    def __init__(self, data_file='../data/books.json'):
        self.data_file = data_file
        self.ensure_data_file()
    
    def ensure_data_file(self):
        if not os.path.exists(self.data_file):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def get_all_books(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_book(self, book_data):
        books = self.get_all_books()
        
        if 'id' not in book_data:
            book_data['id'] = self.generate_id()
        
        book_data['created_at'] = datetime.now().isoformat()
        book_data['updated_at'] = datetime.now().isoformat()
        
        books.append(book_data)
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(books, f, ensure_ascii=False, indent=2)
        
        return book_data
    
    def update_book(self, book_id, book_data):
        books = self.get_all_books()
        
        for i, book in enumerate(books):
            if book.get('id') == book_id:
                book_data['updated_at'] = datetime.now().isoformat()
                books[i] = {**book, **book_data}
                
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(books, f, ensure_ascii=False, indent=2)
                
                return books[i]
        
        return None
    
    def delete_book(self, book_id):
        books = self.get_all_books()
        original_length = len(books)
        
        books = [book for book in books if book.get('id') != book_id]
        
        if len(books) < original_length:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(books, f, ensure_ascii=False, indent=2)
            return True
        
        return False
    
    def get_book_by_id(self, book_id):
        books = self.get_all_books()
        
        for book in books:
            if book.get('id') == book_id:
                return book
        
        return None
    
    def generate_id(self):
        import time
        import random
        return f"{int(time.time())}{random.randint(1000, 9999)}"