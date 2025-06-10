document.addEventListener("DOMContentLoaded", function () {
    const vehicleTypeField = document.getElementById("id_vehicle_type");
    const brandField = document.getElementById("id_brand");
    const modelField = document.getElementById("id_model");
    const modelLoader = document.getElementById("model-loader");

    // Fonction pour charger les marques selon le type de véhicule
    function loadBrands() {
        const type = vehicleTypeField.value.trim();
        brandField.innerHTML = "<option value=''>Chargement...</option>";
        modelField.innerHTML = "<option value=''>Sélectionnez une marque d'abord</option>";

        if (type) {
            fetch(`/vehicles/ajax/get-brands/?vehicle_type=${encodeURIComponent(type)}`)
                .then(res => res.json())
                .then(data => {
                    brandField.innerHTML = "<option value=''>Sélectionnez une marque</option>";
                    data.brands.forEach(brand => {
                        const option = document.createElement("option");
                        option.value = brand;
                        option.textContent = brand;
                        brandField.appendChild(option);
                    });
                })
                .catch(err => {
                    console.error("Erreur chargement des marques :", err);
                    brandField.innerHTML = "<option value=''>Erreur de chargement</option>";
                });
        }
    }

    // Fonction pour charger les modèles
    function loadModels() {
        const marque = brandField.value.trim();
        const type = vehicleTypeField.value.trim();

        modelField.innerHTML = "<option value=''>Chargement...</option>";

        if (marque && type) {
            modelLoader.classList.remove("d-none");

            fetch(`/vehicles/ajax/get-models/?brand=${encodeURIComponent(marque)}&vehicle_type=${encodeURIComponent(type)}`)
                .then(res => res.json())
                .then(data => {
                    modelField.innerHTML = "<option value=''>Sélectionnez un modèle</option>";
                    data.models.forEach(model => {
                        const option = document.createElement("option");
                        option.value = model;
                        option.textContent = model;
                        modelField.appendChild(option);
                    });
                })
                .catch(err => {
                    console.error("Erreur chargement modèles :", err);
                    modelField.innerHTML = "<option value=''>Erreur de chargement</option>";
                })
                .finally(() => modelLoader.classList.add("d-none"));
        } else {
            modelField.innerHTML = "<option value=''>Sélectionnez une marque d'abord</option>";
        }
    }

    // Événements
    vehicleTypeField.addEventListener("change", () => {
        loadBrands();
    });

    brandField.addEventListener("change", loadModels);
});