document.addEventListener("DOMContentLoaded", function () {
    const addVehicleForm = document.getElementById("addVehicleForm");
    const submitLoader = document.getElementById("submit-loader");
    const successNotification = document.getElementById("success-notification");
    const errorNotification = document.getElementById("error-notification");
    const brandField = document.getElementById("id_brand");
    const modelField = document.getElementById("id_model");

    if (!addVehicleForm) return;

    // 🔹 Fonction pour afficher notification
    function showNotification(element, message) {
        element.textContent = message;
        element.classList.remove("hidden");
        setTimeout(() => element.classList.add("hidden"), 3000); // Masquer après 3s
    }

    // 🔹 Charger les modèles dynamiquement selon la marque
    if (brandField && modelField) {
        brandField.addEventListener("change", function () {
            const brand = brandField.value;
            modelField.innerHTML = "<option value=''>Chaje modèl yo...</option>";

            if (!brand) {
                modelField.innerHTML = "<option value=''>Chwazi yon mak avan</option>";
                return;
            }

            fetch(`/vehicles/get_models/?brand=${encodeURIComponent(brand)}`)
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
                    modelField.innerHTML = "<option value=''>Erè pandan chajman</option>";
                    console.error(err);
                });
        });
    }

    // 🔹 Submit Ajax
    addVehicleForm.addEventListener("submit", function (e) {
        e.preventDefault();

        submitLoader.classList.remove("hidden");
        successNotification.classList.add("hidden");
        errorNotification.classList.add("hidden");

        const formData = new FormData(addVehicleForm);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(addVehicleForm.dataset.url, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": csrfToken,
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(res => res.json())
        .then(data => {
            submitLoader.classList.add("hidden");

            if (data.success) {
                showNotification(successNotification, data.message || "Machin anrejistre avèk siksè !");
                // Redirection après 1s
                if (data.redirect_url) {
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 1000);
                }
            } else {
                let msg = data.message || "Erè pandan anrejistreman machin nan.";
                if (data.errors) {
                    msg += "\n" + JSON.stringify(data.errors);
                }
                showNotification(errorNotification, msg);
            }
        })
        .catch(err => {
            submitLoader.classList.add("hidden");
            showNotification(errorNotification, "Erè rezo. Tanpri eseye ankò.");
            console.error(err);
        });
    });
});