document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("orderSearchInput");
    const orderCards = document.querySelectorAll(".order-card");
    const noOrderResult = document.getElementById("noOrderResult");

    if (!searchInput || !orderCards.length) return;

    function filterOrders() {
        const keyword = searchInput.value.trim().toLowerCase();
        let visibleCount = 0;

        orderCards.forEach(function (card) {
            const code = (card.dataset.orderCode || "").toLowerCase();
            const status = (card.dataset.orderStatus || "").toLowerCase();

            const matched = code.includes(keyword) || status.includes(keyword);

            if (matched) {
                card.style.display = "";
                visibleCount++;
            } else {
                card.style.display = "none";
            }
        });

        if (noOrderResult) {
            noOrderResult.style.display = visibleCount === 0 ? "block" : "none";
        }
    }

    searchInput.addEventListener("input", filterOrders);
});