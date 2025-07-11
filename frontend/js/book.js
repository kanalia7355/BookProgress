class Book {
    constructor(data) {
        this.id = data.id || this.generateId();
        this.isbn = data.isbn;
        this.title = data.title;
        this.author = data.author || '';
        this.totalPages = data.totalPages || 0;
        this.currentPage = data.currentPage || 0;
        this.coverImage = data.coverImage || '';
        this.readingTime = data.readingTime || 0;
        this.timer = new Timer(this.id, this.readingTime);
    }

    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    getProgress() {
        if (this.totalPages === 0) return 0;
        return Math.round((this.currentPage / this.totalPages) * 100);
    }

    updateProgress(currentPage) {
        this.currentPage = Math.max(0, Math.min(currentPage, this.totalPages));
        window.bookApp.updateBook(this.id, { currentPage: this.currentPage });
    }

    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    render() {
        const progress = this.getProgress();
        const coverImageSrc = this.coverImage || '';
        
        return `
            <div class="book-item" data-book-id="${this.id}">
                <div class="book-cover">
                    ${coverImageSrc ? `<img src="${coverImageSrc}" alt="書籍カバー">` : '画像なし'}
                </div>
                <div class="book-info">
                    <div class="book-title">${this.title}</div>
                    <div class="book-details">
                        <p><strong>著者:</strong> ${this.author}</p>
                        <p><strong>ページ数:</strong> ${this.currentPage}/${this.totalPages}</p>
                        <p><strong>読書時間:</strong> <span class="timer-display" id="timer-${this.id}">${this.formatTime(this.readingTime)}</span></p>
                    </div>
                    <div class="progress-section">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${progress}%"></div>
                        </div>
                        <div class="progress-text">${progress}% 完了</div>
                    </div>
                    <div class="reading-controls">
                        <button class="control-btn start-btn" data-action="start">開始</button>
                        <button class="control-btn stop-btn" data-action="stop">停止</button>
                        <button class="control-btn reset-btn" data-action="reset">リセット</button>
                        <input type="number" class="page-input" 
                               placeholder="ページ" 
                               min="0" 
                               max="${this.totalPages}"
                               value="${this.currentPage}">
                        <button class="control-btn update-btn" data-action="update">更新</button>
                    </div>
                </div>
            </div>
        `;
    }

    bindEvents() {
        const bookElement = document.querySelector(`[data-book-id="${this.id}"]`);
        if (!bookElement) return;

        const startBtn = bookElement.querySelector('[data-action="start"]');
        const stopBtn = bookElement.querySelector('[data-action="stop"]');
        const resetBtn = bookElement.querySelector('[data-action="reset"]');
        const updateBtn = bookElement.querySelector('[data-action="update"]');
        const pageInput = bookElement.querySelector('.page-input');

        startBtn.addEventListener('click', () => {
            this.timer.start();
            this.updateTimerDisplay();
        });

        stopBtn.addEventListener('click', () => {
            this.timer.stop();
            this.readingTime = this.timer.getTotalTime();
            window.bookApp.updateBook(this.id, { readingTime: this.readingTime });
        });

        resetBtn.addEventListener('click', () => {
            if (confirm('読書時間をリセットしますか？')) {
                this.timer.reset();
                this.readingTime = 0;
                this.updateTimerDisplay();
                window.bookApp.updateBook(this.id, { readingTime: this.readingTime });
            }
        });

        updateBtn.addEventListener('click', () => {
            const newPage = parseInt(pageInput.value) || 0;
            this.updateProgress(newPage);
        });

        pageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const newPage = parseInt(pageInput.value) || 0;
                this.updateProgress(newPage);
            }
        });

        this.timer.onTick = () => {
            this.updateTimerDisplay();
        };
    }

    updateTimerDisplay() {
        const timerElement = document.getElementById(`timer-${this.id}`);
        if (timerElement) {
            timerElement.textContent = this.formatTime(this.timer.getTotalTime());
        }
    }

    toJSON() {
        return {
            id: this.id,
            isbn: this.isbn,
            title: this.title,
            author: this.author,
            totalPages: this.totalPages,
            currentPage: this.currentPage,
            coverImage: this.coverImage,
            readingTime: this.readingTime
        };
    }

    static fromJSON(data) {
        return new Book(data);
    }
}