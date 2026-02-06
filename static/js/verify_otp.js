// static/js/verify_otp.js

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#verify-otp-form");
    const resendBtn = document.querySelector("#resend-otp-btn");
    const countdownDisplay = document.querySelector("#otp-countdown");

    // ✅ Gestion du formulaire OTP
    if (form) {
        form.addEventListener("submit", function (e) {
            const otpField = document.querySelector("#otp-input");
            if (!otpField.value.trim()) {
                e.preventDefault();
                alert("Veuillez entrer le code OTP.");
                return false;
            }

            // Désactive le bouton pour éviter plusieurs clics
            const submitBtn = form.querySelector("button[type='submit']");
            submitBtn.disabled = true;
            submitBtn.innerText = "Vérification...";
        });
    }

    // 🔄 Gestion du bouton de renvoi OTP
    if (resendBtn && countdownDisplay) {
        let countdown = 60; // 60 secondes avant de pouvoir renvoyer

        const startCountdown = () => {
            resendBtn.disabled = true;
            const timer = setInterval(() => {
                countdownDisplay.textContent = `Vous pourrez renvoyer un code dans ${countdown}s`;
                countdown--;
                if (countdown < 0) {
                    clearInterval(timer);
                    resendBtn.disabled = false;
                    countdownDisplay.textContent = "";
                }
            }, 1000);
        };

        resendBtn.addEventListener("click", function (e) {
            e.preventDefault();
            fetch(resendBtn.dataset.url)
                .then(response => {
                    if (response.ok) {
                        alert("Nouveau code OTP envoyé !");
                        countdown = 60;
                        startCountdown();
                    } else {
                        alert("Erreur lors de l’envoi du code OTP.");
                    }
                })
                .catch(() => alert("Erreur de connexion."));
        });

        startCountdown();
    }
});