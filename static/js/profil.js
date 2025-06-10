document.addEventListener("DOMContentLoaded", function() {
    let activeTab = localStorage.getItem("activeTab") || "#info";
    let tab = document.querySelector(`a[href="${activeTab}"]`);
    if (tab) {
        new bootstrap.Tab(tab).show();
    }

    document.querySelectorAll('.nav-tabs a').forEach(tab => {
        tab.addEventListener("click", function() {
            localStorage.setItem("activeTab", this.getAttribute("href"));
        });
    });
});