document.addEventListener("DOMContentLoaded", function () {
    const images = document.querySelectorAll(".carousel-images img");
    const prevButton = document.querySelector(".prev");
    const nextButton = document.querySelector(".next");
    let currentIndex = 0;

    // Affiche l'image actuelle
    function showImage(index) {
        images.forEach((img, i) => {
            img.classList.toggle("active", i === index);
        });
    }

    // Bouton suivant
    nextButton.addEventListener("click", () => {
        currentIndex = (currentIndex + 1) % images.length;
        showImage(currentIndex);
    });

    // Bouton précédent
    prevButton.addEventListener("click", () => {
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        showImage(currentIndex);
    });

    // Affiche la première image au chargement
    showImage(currentIndex);
});