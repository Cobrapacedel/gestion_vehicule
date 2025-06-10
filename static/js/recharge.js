document.addEventListener("DOMContentLoaded", function () {
        const montantInput = document.getElementById("id_montant");
        const deviseInputs = document.querySelectorAll("input[name='devise']");
        const summaryBox = document.getElementById("summary");
        const summaryMontant = document.getElementById("summary-montant");
        const summaryDevise = document.getElementById("summary-devise");

        function updateSummary() {
            let montant = montantInput.value;
            let selectedDevise = document.querySelector("input[name='devise']:checked");

            if (montant && selectedDevise) {
                summaryMontant.textContent = montant;
                summaryDevise.textContent = selectedDevise.value;
                summaryBox.classList.remove("d-none");
            } else {
                summaryBox.classList.add("d-none");
            }
        }

        montantInput.addEventListener("input", updateSummary);
        deviseInputs.forEach(input => input.addEventListener("change", updateSummary));
    });
    
    document.getElementById("recharge-form").addEventListener("submit", function(event) {
        event.preventDefault();  // Empêche la soumission immédiate du formulaire
        window.location.href = "{% url 'payments:choose_platform' %}";  // Redirige après validation
    });
