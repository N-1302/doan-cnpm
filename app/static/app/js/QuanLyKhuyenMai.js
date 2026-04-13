document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("promoModal");
    const openBtn = document.getElementById("openPromoModal");
    const closeBtn = document.getElementById("closePromoModal");
    const cancelBtn = document.getElementById("cancelPromoModal");

    if (openBtn) {
        openBtn.addEventListener("click", function () {
            modal.classList.add("show");
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener("click", function () {
            modal.classList.remove("show");
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener("click", function () {
            modal.classList.remove("show");
        });
    }

    window.addEventListener("click", function (e) {
        if (e.target === modal) {
            modal.classList.remove("show");
        }
    });
});