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
        const addBookBtn = document.getElementById('add-book-btn');
        const isbn = isbnInput.value.trim();

        if (!isbn) {
            alert('ISBNコードを入力してください');
            return;
        }

        if (!this.validateISBN(isbn)) {
            alert('正しいISBNコードを入力してください（10桁または13桁の数字）');
            return;
        }

        // ボタンを無効化してローディング状態に
        addBookBtn.disabled = true;
        addBookBtn.textContent = '取得中...';

        try {
            console.log(`書籍データを取得中: ${isbn}`);
            const bookData = await this.fetchBookData(isbn);
            
            if (bookData) {
                console.log('書籍データ取得成功:', bookData);
                const book = new Book(bookData);
                this.books.push(book);
                this.saveBooks();
                this.renderBooks();
                isbnInput.value = '';
                alert(`書籍「${bookData.title}」を追加しました`);
            }
        } catch (error) {
            console.error('書籍データの取得に失敗しました:', error);
            
            // より詳細なエラーメッセージを表示
            let errorMessage = '書籍データの取得に失敗しました';
            if (error.message) {
                errorMessage += `: ${error.message}`;
            }
            alert(errorMessage);
        } finally {
            // ボタンを元に戻す
            addBookBtn.disabled = false;
            addBookBtn.textContent = '書籍を追加';
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
            
            console.log(`API URL: ${apiUrl}`);
            
            const response = await fetch(apiUrl);
            console.log(`Response status: ${response.status}`);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.message || errorData.error || `HTTP ${response.status}`;
                throw new Error(errorMessage);
            }
            
            const data = await response.json();
            console.log('API response data:', data);
            
            return data;
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