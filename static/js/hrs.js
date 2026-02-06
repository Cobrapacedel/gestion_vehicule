    function updateDateTime() {
        const dateEl = document.getElementById('date');
        const timeEl = document.getElementById('time');
        const now = new Date();
        const weekdaysHT = ['Dimanch', 'Lendi', 'Madi', 'Mèkredi', 'Jedi', 'Vandredi', 'Samdi'];
        const monthsHT = ['Janvye', 'Fevriye', 'Mas', 'Avril', 'Me', 'Jen', 'Jiyè', 'Out', 'Septanm', 'Oktòb', 'Novanm', 'Desanm'];
        const weekday = weekdaysHT[now.getDay()];
        const day = now.getDate();
        const month = monthsHT[now.getMonth()];
        const year = now.getFullYear();
        dateEl.textContent = `${weekday} ${day} ${month} ${year}`;
        let hours = now.getHours();
        const minutes = now.getMinutes().toString().padStart(2,'0');
        const seconds = now.getSeconds().toString().padStart(2,'0');
        let period;
        if(hours >=1 && hours<12) period='(maten)';
        else if(hours===12) period='(midi)';
        else if(hours>12 && hours<19) period='(aprèmidi)';
        else if(hours>=19 && hours<=23) period='(aswè)';
        else period='(minwi)';
        const displayHours = hours%12||12;
        timeEl.textContent = `${displayHours}:${minutes}:${seconds} ${period}`;
    }