document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("orderSearchInput");
    const orderCards = document.querySelectorAll(".order-card");
    const noResultBox = document.getElementById("noOrderResult");

    function parsePrice(value) {
        if (value === null || value === undefined) return 0;

        let raw = String(value).trim();
        if (!raw) return 0;

        raw = raw.replace(/đ|vnd|vnđ/gi, "").trim();

        const directNumber = Number(raw);
        if (!Number.isNaN(directNumber)) {
            return Math.round(directNumber);
        }

        if (/^\d{1,3}([.,]\d{3})+([.,]\d+)?$/.test(raw)) {
            raw = raw.replace(/[.,](?=\d{3}\b)/g, "");
        }

        raw = raw.replace(",", ".");

        const parsed = parseFloat(raw);
        if (!Number.isNaN(parsed)) {
            return Math.round(parsed);
        }

        return 0;
    }

    function formatMoney(value) {
        return parsePrice(value).toLocaleString("vi-VN") + " đ";
    }

    function applyFormatPrice() {
        document.querySelectorAll(".format-price").forEach(function (el) {
            const rawValue = el.getAttribute("data-price");
            console.log("data-price =", rawValue);
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