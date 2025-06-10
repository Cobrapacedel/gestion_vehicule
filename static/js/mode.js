document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("mode-toggle");
    const modeIcon = document.getElementById("mode-icon");
    const body = document.body;

    if (!toggleButton || !modeIcon) {
        console.error("Bouton ou icône de mode sombre introuvable !");
        return;
    }

    // Vérifier si un mode est déjà enregistré dans localStorage
    if (localStorage.getItem("theme") === "dark") {
        activerModeSombre();
    }

    // Écouteur d'événement sur le bouton
    toggleButton.addEventListener("click", function () {
        if (body.classList.contains("dark-mode")) {
            desactiverModeSombre();
        } else {
            activerModeSombre();
        }
    });

    function activerModeSombre() {
        body.classList.add("dark-mode");
        modeIcon.classList.replace("fa-moon", "fa-sun");
        toggleButton.classList.replace("btn-light", "btn-dark");
        localStorage.setItem("theme", "dark");
    }

    function desactiverModeSombre() {
        body.classList.remove("dark-mode");
        modeIcon.classList.replace("fa-sun", "fa-moon");
        toggleButton.classList.replace("btn-dark", "btn-light");
        localStorage.setItem("theme", "light");
    }
});
document.addEventListener("DOMContentLoaded", function () {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});