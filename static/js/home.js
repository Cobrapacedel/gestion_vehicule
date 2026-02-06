document.addEventListener('alpine:init', () => {
    Alpine.data('homePage', () => ({
        active: 0,
        images: [
            '/static/images/truck1.png',
            '/static/images/moto1.png',
            '/static/images/bus1.png',
            '/static/images/voiture2.png',
            '/static/images/moto2.png',
            '/static/images/bus2.png'
        ],
        darkMode: localStorage.getItem('darkMode') === 'enabled',
        x: parseFloat(localStorage.getItem("darkModeX")) || 20,
        y: parseFloat(localStorage.getItem("darkModeY")) || 20,
        dragging: false,
        offsetX: 0,
        offsetY: 0,

        init() {
            // Appliquer le mode sombre si besoin
            if (this.darkMode) document.documentElement.classList.add('dark');
            lucide.createIcons();

            // Carousel automatique
            setInterval(() => {
                this.active = (this.active + 1) % this.images.length;
            }, 4000);

            // Horloge
            this.updateDateTime();
            setInterval(() => this.updateDateTime(), 1000);

            // Suivi du mouvement pour le bouton draggable
            window.addEventListener('mousemove', e => this.drag(e));
            window.addEventListener('touchmove', e => this.drag(e));
        },

        start(e) {
            this.dragging = true;
            const point = e.touches ? e.touches[0] : e;
            this.offsetX = point.clientX - this.x;
            this.offsetY = point.clientY - this.y;
            if (e.cancelable) e.preventDefault();
        },

        drag(e) {
            if (!this.dragging) return;
            const point = e.touches ? e.touches[0] : e;
            this.x = Math.max(0, Math.min(window.innerWidth - 60, point.clientX - this.offsetX));
            this.y = Math.max(0, Math.min(window.innerHeight - 60, point.clientY - this.offsetY));
        },

        stop() {
            this.dragging = false;
            localStorage.setItem("darkModeX", this.x);
            localStorage.setItem("darkModeY", this.y);
        },

        toggleDarkMode() {
            this.darkMode = !this.darkMode;
            document.documentElement.classList.toggle('dark', this.darkMode);
            localStorage.setItem('darkMode', this.darkMode ? 'enabled' : 'disabled');
            lucide.createIcons();
        },

        updateDateTime() {
            const now = new Date();
            const dateEl = document.getElementById('date');
            const timeEl = document.getElementById('time');
            if (dateEl) {
                dateEl.textContent = now.toLocaleDateString('fr-FR', {
                    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
                });
            }
            if (timeEl) {
                timeEl.textContent = now.toLocaleTimeString('fr-FR', {
                    hour: '2-digit', minute: '2-digit', second: '2-digit'
                });
            }
        }
    }));
});