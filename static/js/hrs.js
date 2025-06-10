        // Scroll to footer if ?scroll=footer
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('scroll') && urlParams.get('scroll') === 'footer') {
            document.getElementById('footer').scrollIntoView({ behavior: 'smooth' });
        }

        // Heure et date dynamique
    function updateTime() {
        const now = new Date();
        const optionsDate = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            timeZone: 'America/Port-au-Prince'  // Pour Haïti
        };
        const optionsTime = {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false,
            timeZone: 'America/Port-au-Prince'
        };

        document.getElementById("date").textContent = now.toLocaleDateString("fr-FR", optionsDate);
        document.getElementById("time").textContent = now.toLocaleTimeString("fr-FR", optionsTime);
    }

    setInterval(updateTime, 1000);
    updateTime();