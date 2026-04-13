document.addEventListener("DOMContentLoaded", function () {
    const cards = document.querySelectorAll(".ad-feature-card, .ad-stat-card, .ad-panel");

    cards.forEach((card, index) => {
        card.style.opacity = "0";
        card.style.transform = "translateY(14px)";
        card.style.transition = "all 0.4s ease";

        setTimeout(() => {
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
        }, 80 * index);
    });
});