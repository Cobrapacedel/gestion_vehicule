document.addEventListener("DOMContentLoaded", function () {
    const vehicleTypeField = document.getElementById("id_vehicle_type");
    const brandField = document.getElementById("id_brand");
    const modelField = document.getElementById("id_model");
    const modelLoader = document.getElementById("model-loader");
    const form = document.getElementById("addVehicleForm");
    const successNotification = document.getElementById("success-notification");
    const errorNotification = document.getElementById("error-notification");

    // Charger marques selon type
    vehicleTypeField.addEventListener("change", function () {
        const type = vehicleTypeField.value;
        brandField.innerHTML = "<option value=''>Tann...</option>";
        modelField.innerHTML = "<option value=''>Chwazi yon modèl</option>";

        if (type) {
            fetch(`/vehicles/ajax/get-brands/?vehicle_type=${encodeURIComponent(type)}`)
                .then(res => res.json())
                .then(data => {
                    brandField.innerHTML = "<option value=''>Chwazi yon mak</option>";
                    data.brands.forEach(brand => {
                        const option = document.createElement("option");
                        option.value = brand;
                        option.textContent = brand;
                        brandField.appendChild(option);
                    });
                })
                .catch(err => {
                    console.error(err);
                    brandField.innerHTML = "<option value=''>Erè</option>";
                });
        }
    });

    // Charger modèles selon marque et type
    brandField.addEventListener("change", function () {
        const type = vehicleTypeField.value;
        const brand = brandField.value;
        modelField.innerHTML = "<option value=''>Tann...</option>";
        modelLoader.classList.remove("hidden");

        fetch(`/vehicles/ajax/get-models/?vehicle_type=${encodeURIComponent(type)}&brand=${encodeURIComponent(brand)}`)
            .then(res => res.json())
            .then(data => {
                modelField.innerHTML = "<option value=''>Chwazi yon modèl</option>";
                data.models.forEach(model => {
                    const option = document.createElement("option");
                    option.value = model;
                    option.textContent = model;
                    modelField.appendChild(option);
                });
            })
            .catch(err => {
                console.error(err);
                modelField.innerHTML = "<option value=''>Erè de chargement</option>";
            })
            .finally(() => modelLoader.classList.add("hidden"));
    });

    // Submit Ajax
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        successNotification.classList.add("hidden");
        errorNotification.classList.add("hidden");

        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(form.dataset.url, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": csrfToken,
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                successNotification.textContent = data.message;
                successNotification.classList.remove("hidden");
                if (data.redirect_url) {
                    setTimeout(() => { window.location.href = data.redirect_url; }, 1000);
                }
            } else {
                console.error("Erreurs:", data.errors);
                errorNotification.textContent = data.message;
                errorNotification.classList.remove("hidden");
            }
        })
        .catch(err => {
            errorNotification.textContent = "Erè rezo, tanpri eseye ankò.";
            errorNotification.classList.remove("hidden");
            console.error(err);
        });
    });
});