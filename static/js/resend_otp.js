        document.getElementById("resend-otp-btn").addEventListener("click", function () {
            // Disable the button to prevent multiple clicks
            this.disabled = true;
            this.textContent = "Renvoi en cours...";

            // Send POST request to resend OTP
            fetch("{% url 'resend-otp' %}", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": "{{ csrf_token }}", // Include CSRF token for security
                },
            })
            .then(response => response.json())
            .then(data => {
                const otpMessage = document.getElementById("otp-message");
                otpMessage.classList.remove("d-none");

                if (data.status === "success") {
                    otpMessage.innerHTML = `<p class="text-success">${data.message}</p>`;
                } else {
                    otpMessage.innerHTML = `<p class="text-danger">${data.message}</p>`;
                }
            })
            .catch(error => {
                console.error("Error:", error);
                document.getElementById("otp-message").innerHTML =
                    '<p class="text-danger">Une erreur s\'est produite. Veuillez réessayer.</p>';
            })
            .finally(() => {
                // Re-enable the button
                this.disabled = false;
                this.textContent = "Renvoyer OTP";
            });
        });