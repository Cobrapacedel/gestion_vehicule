document.addEventListener("DOMContentLoaded", () => {

    const realUser = document.getElementById("id_real_user");
    const clientType = document.getElementById("id_client_type");

    const wrapClientType = document.getElementById("wrap_client_type");
    const simpleFields = document.getElementById("simple_fields");
    const businessFields = document.getElementById("business_fields");

    function reset() {
        simpleFields.classList.add("hidden");
        businessFields.classList.add("hidden");
    }

    function updateClientForm() {
        reset();

        if (realUser.value) {
            wrapClientType.style.display = "none";
            return;
        }

        wrapClientType.style.display = "block";

        if (clientType.value === "user") {
            simpleFields.classList.remove("hidden");
        }

        if (["dealer", "agency", "garage"].includes(clientType.value)) {
            businessFields.classList.remove("hidden");
        }
    }

    realUser.addEventListener("change", updateClientForm);
    clientType.addEventListener("change", updateClientForm);

    updateClientForm();
});