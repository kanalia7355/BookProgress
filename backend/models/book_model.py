from datetime import datetime
from typing import Dict, Optional

class BookModel:
    def __init__(self, data: Dict):
        self.id = data.get('id')
        self.isbn = data.get('isbn', '')
        self.title = data.get('title', '')
        self.author = data.get('author', '')
        self.publisher = data.get('publisher', '')
        self.pubdate = data.get('pubdate', '')
        self.total_pages = data.get('totalPages', 0)
        self.current_page = data.get('currentPage', 0)
        self.cover_image = data.get('coverImage', '')
        self.reading_time = data.get('readingTime', 0)
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'publisher': self.publisher,
            'pubdate': self.pubdate,
            'totalPages': self.total_pages,
            'currentPage': self.current_page,
            'coverImage': self.cover_image,
            'readingTime': self.reading_time,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def get_progress_percentage(self) -> float:
        if self.total_pages == 0:
            return 0.0
        return (self.current_page / self.total_pages) * 100
    
    def is_completed(self) -> bool:
        return self.current_page >= self.total_pages
    
    def update_progress(self, current_page: int) -> None:
        self.current_page = max(0, min(current_page, self.total_pages))
        self.updated_at = datetime.now().isoformat()
    
    def update_reading_time(self, reading_time: int) -> None:
        self.reading_time = max(0, reading_time)
        self.updated_at = datetime.now().isoformat()
    
    @classmethod
    def from_api_data(cls, api_data: Dict) -> 'BookModel':
        return cls(api_data)
    
    def __str__(self) -> str:
        return f"BookModel(id={self.id}, title='{self.title}', progress={self.get_progress_percentage():.1f}%)"
    
    def __repr__(self) -> str:
        return self.__str__()