document.addEventListener("DOMContentLoaded", function () {
    const marqueField = document.getElementById("id_marque");
    const modeleField = document.getElementById("id_modele");
    const vehicleList = document.getElementById("vehicleList");
    const addVehicleForm = document.getElementById("addVehicleForm");

    // Vérifie si les éléments DOM existent
    if (!marqueField || !modeleField || !vehicleList || !addVehicleForm) {
        console.error("Un ou plusieurs éléments DOM sont manquants.");
        return;
    }

    // Charger les modèles quand la marque change
    marqueField.addEventListener("change", function () {
        const marque = marqueField.value.trim();
        modeleField.innerHTML = "<option value=''>Chargement...</option>";

        if (marque) {
            fetch(`/vehicles/get-models/?brand=${encodeURIComponent(marque)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Erreur HTTP : ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    modeleField.innerHTML = "<option value=''>Sélectionnez un modèle</option>";
                    if (data.models && data.models.length > 0) {
                        data.models.forEach(modele => {
                            const option = document.createElement("option");
                            option.value = modele;
                            option.textContent = modele;
                            modeleField.appendChild(option);
                        });
                    } else {
                        modeleField.innerHTML = "<option value=''>Aucun modèle disponible</option>";
                    }
                })
                .catch(error => {
                    modeleField.innerHTML = "<option value=''>Erreur de chargement</option>";
                    console.error("Erreur AJAX :", error);
                });
        } else {
            modeleField.innerHTML = "<option value=''>Sélectionnez une marque d'abord</option>";
        }
    });

    // Gestion de l'ajout d'un véhicule
    addVehicleForm.addEventListener("submit", function (event) {
        event.preventDefault(); // Empêcher le rechargement de la page

        const formData = new FormData(addVehicleForm);

        // Inclure le jeton CSRF dans la requête AJAX
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch("{% url 'vehicles:add_vehicle' %}", {
            method: "POST",
            body: formData,
            headers: { "X-CSRFToken": csrfToken, "X-Requested-With": "XMLHttpRequest" }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur HTTP : ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.id) {
                    const newVehicle = document.createElement("li");
                    newVehicle.textContent = `${data.brand} - ${data.model} (${data.year}) - ${data.color}`;
                    vehicleList.appendChild(newVehicle);
                    addVehicleForm.reset();

                    // Afficher un message de succès
                    alert("Véhicule ajouté avec succès !");
                } else if (data.errors) {
                    // Afficher les erreurs de validation
                    alert("Erreur(s) de validation : " + Object.values(data.errors).join(", "));
                }
            })
            .catch(error => {
                alert("Erreur de connexion : " + error.message);
                console.error("Erreur AJAX :", error);
            });
    });

    // Validation client-side avec Bootstrap
    (function () {
        'use strict';
        const forms = document.querySelectorAll('.needs-validation');
        Array.prototype.slice.call(forms).forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    })();
});