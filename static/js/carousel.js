document.addEventListener("DOMContentLoaded", function () {
    let carousel = new bootstrap.Carousel(document.getElementById("carrousel-voitures"), {
        interval: 2000,  // Change d'image toutes les 2 secondes
        wrap: true       // Continue en boucle
    });
});