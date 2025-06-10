document.addEventListener("DOMContentLoaded", function () {

    // Fonction pour ouvrir le modal de recharge
    function openRechargeModal(currency) {
        document.getElementById("currencyType").value = currency;
        new bootstrap.Modal(document.getElementById("rechargeModal")).show();
    }

    // Gestion du formulaire de recharge
    document.getElementById("rechargeForm").addEventListener("submit", function (event) {
        event.preventDefault();
        let currency = document.getElementById("currencyType").value;
        let amount = document.getElementById("amount").value;

        if (amount <= 0 || isNaN(amount)) {
            alert("Veuillez entrer un montant valide.");
            return;
        }

        alert("Recharge de " + amount + " " + currency + " en cours...");
        // Ici, tu peux ajouter un appel AJAX pour envoyer la demande au serveur.
    });

    // Fonction pour afficher/masquer le solde avec animation fluide
    function toggleBalance(currency) {
        let balanceElement = document.getElementById("balance-" + currency);
        let iconElement = document.getElementById("toggle-" + currency);

        balanceElement.classList.add("hidden"); // Effet de transition
        setTimeout(() => {
            if (balanceElement.innerText === "*****") {
                balanceElement.innerText = balanceElement.getAttribute("data-real-value");
                iconElement.classList.replace("bi-eye", "bi-eye-slash");
            } else {
                balanceElement.innerText = "*****";
                iconElement.classList.replace("bi-eye-slash", "bi-eye");
            }
            balanceElement.classList.remove("hidden");
        }, 300);
    }

    // Rendre `toggleBalance` accessible globalement
    window.openRechargeModal = openRechargeModal;
    window.toggleBalance = toggleBalance;

});