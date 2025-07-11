class BookApp {
    constructor() {
        this.books = [];
        this.init();
    }

    init() {
        this.loadBooks();
        this.bindEvents();
        this.renderBooks();
    }

    bindEvents() {
        const addBookBtn = document.getElementById('add-book-btn');
        const isbnInput = document.getElementById('isbn-input');

        addBookBtn.addEventListener('click', () => this.addBook());
        isbnInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.addBook();
            }
        });
    }

    async addBook() {
        const isbnInput = document.getElementById('isbn-input');
        const isbn = isbnInput.value.trim();

        if (!isbn) {
            alert('ISBNコードを入力してください');
            return;
        }

        if (!this.validateISBN(isbn)) {
            alert('正しいISBNコードを入力してください');
            return;
        }

        try {
            const bookData = await this.fetchBookData(isbn);
            if (bookData) {
                const book = new Book(bookData);
                this.books.push(book);
                this.saveBooks();
                this.renderBooks();
                isbnInput.value = '';
            }
        } catch (error) {
            console.error('書籍データの取得に失敗しました:', error);
            alert('書籍データの取得に失敗しました');
        }
    }

    validateISBN(isbn) {
        const cleanISBN = isbn.replace(/[-\s]/g, '');
        return cleanISBN.length === 10 || cleanISBN.length === 13;
    }

    async fetchBookData(isbn) {
        try {
            const apiUrl = window.location.hostname === 'localhost' 
                ? `http://localhost:5000/api/book/${isbn}`
                : `/api/book/${isbn}`;
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error('書籍情報が見つかりません');
            }
            return await response.json();
        } catch (error) {
            console.error('API呼び出しエラー:', error);
            throw error;
        }
    }

    renderBooks() {
        const booksList = document.getElementById('books-list');
        
        if (this.books.length === 0) {
            booksList.innerHTML = '<p class="no-books">まだ書籍が登録されていません</p>';
            return;
        }

        booksList.innerHTML = this.books.map(book => book.render()).join('');
        
        this.books.forEach(book => {
            book.bindEvents();
        });
    }

    saveBooks() {
        const booksData = this.books.map(book => book.toJSON());
        localStorage.setItem('books', JSON.stringify(booksData));
    }

    loadBooks() {
        const savedBooks = localStorage.getItem('books');
        if (savedBooks) {
            const booksData = JSON.parse(savedBooks);
            this.books = booksData.map(data => Book.fromJSON(data));
        }
    }

    removeBook(bookId) {
        this.books = this.books.filter(book => book.id !== bookId);
        this.saveBooks();
        this.renderBooks();
    }

    updateBook(bookId, updates) {
        const book = this.books.find(b => b.id === bookId);
        if (book) {
            Object.assign(book, updates);
            this.saveBooks();
            this.renderBooks();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.bookApp = new BookApp();
});