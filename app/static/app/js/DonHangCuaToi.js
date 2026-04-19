document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("orderSearchInput");
    const orderCards = document.querySelectorAll(".order-card");
    const noResultBox = document.getElementById("noOrderResult");

    function parsePrice(value) {
        if (value === null || value === undefined) return 0;

        const raw = String(value).trim();
        if (!raw) return 0;

        const number = Number(raw);
        if (!Number.isNaN(number)) {
            return Math.round(number);
        }

        const cleaned = raw.replace(/[^\d]/g, "");
        return cleaned ? parseInt(cleaned, 10) : 0;
    }

    function formatMoney(value) {
        return parsePrice(value).toLocaleString("vi-VN") + " đ";
    }

    function applyFormatPrice() {
        document.querySelectorAll(".format-price").forEach(function (el) {
            const rawValue = el.getAttribute("data-price");
            el.textContent = formatMoney(rawValue);
        });
    }

    function filterOrders() {
        if (!searchInput) return;

        const keyword = searchInput.value.trim().toLowerCase();
        let visibleCount = 0;

        orderCards.forEach(function (card) {
            const orderCode = (card.getAttribute("data-order-code") || "").toLowerCase();
            const orderStatus = (card.getAttribute("data-order-status") || "").toLowerCase();

            const matched =
                orderCode.includes(keyword) ||
                orderStatus.includes(keyword);

            card.style.display = matched ? "" : "none";

            if (matched) visibleCount++;
        });

        if (noResultBox) {
            noResultBox.style.display = visibleCount === 0 ? "block" : "none";
        }
    }

    applyFormatPrice();

    if (searchInput) {
        searchInput.addEventListener("input", filterOrders);
    }


    function filterOrders() {
        if (!searchInput) return;

        const keyword = searchInput.value.trim().toLowerCase();
        let visibleCount = 0;

        orderCards.forEach(function (card) {
            const orderCode = (card.getAttribute("data-order-code") || "").toLowerCase();
            const orderStatus = (card.getAttribute("data-order-status") || "").toLowerCase();

            const isMatch = orderCode.includes(keyword) || orderStatus.includes(keyword);

            card.style.display = isMatch ? "" : "none";

            if (isMatch) visibleCount++;
        });

        if (noResultBox) {
            noResultBox.style.display = visibleCount === 0 ? "block" : "none";
        }
    }

    applyFormatPrice();

    if (searchInput) {
        searchInput.addEventListener("input", filterOrders);
    }
});