function draggableDarkMode() {
    return {
        x: parseFloat(localStorage.getItem('darkButtonX')) || 20,
        y: parseFloat(localStorage.getItem('darkButtonY')) || 100,
        dragging: false,
        offsetX: 0,
        offsetY: 0,
        darkMode: localStorage.getItem('darkMode') === 'enabled',

        init() {
            if (this.darkMode) {
                document.documentElement.classList.add('dark');
            },

        start(event) {
            this.dragging = true;
            const e = event.touches ? event.touches[0] : event;
            this.offsetX = e.clientX - this.x;
            this.offsetY = e.clientY - this.y;
        },

        drag(event) {
            if (!this.dragging) return;
            const e = event.touches ? event.touches[0] : event;
            this.x = e.clientX - this.offsetX;
            this.y = e.clientY - this.offsetY;

            // Empêcher de sortir de l'écran
            this.x = Math.max(0, Math.min(window.innerWidth - 60, this.x));
            this.y = Math.max(0, Math.min(window.innerHeight - 60, this.y));
        },

        stop() {
            this.dragging = false;
            localStorage.setItem('darkButtonX', this.x);
            localStorage.setItem('darkButtonY', this.y);
        },

        toggleDarkMode() {
            this.darkMode = !this.darkMode;
            document.documentElement.classList.toggle('dark', this.darkMode);
            localStorage.setItem('darkMode', this.darkMode ? 'enabled' : 'disabled');
            lucide.createIcons();
        },
    };
}