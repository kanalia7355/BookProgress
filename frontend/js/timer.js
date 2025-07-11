class Timer {
    constructor(bookId, initialTime = 0) {
        this.bookId = bookId;
        this.totalTime = initialTime;
        this.startTime = null;
        this.isRunning = false;
        this.interval = null;
        this.onTick = null;
    }

    start() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        this.startTime = Date.now();
        
        this.interval = setInterval(() => {
            this.tick();
        }, 1000);
    }

    stop() {
        if (!this.isRunning) return;
        
        this.isRunning = false;
        
        if (this.startTime) {
            const sessionTime = Math.floor((Date.now() - this.startTime) / 1000);
            this.totalTime += sessionTime;
        }
        
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
        
        this.startTime = null;
    }

    reset() {
        this.stop();
        this.totalTime = 0;
        if (this.onTick) {
            this.onTick();
        }
    }

    tick() {
        if (this.onTick) {
            this.onTick();
        }
    }

    getTotalTime() {
        if (this.isRunning && this.startTime) {
            const sessionTime = Math.floor((Date.now() - this.startTime) / 1000);
            return this.totalTime + sessionTime;
        }
        return this.totalTime;
    }

    getFormattedTime() {
        const totalSeconds = this.getTotalTime();
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    isActive() {
        return this.isRunning;
    }
}