document.addEventListener("DOMContentLoaded", function () {
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
        const priceElements = document.querySelectorAll(".format-price");

        priceElements.forEach(function (el) {
            const rawValue = el.getAttribute("data-price") || el.textContent;
            el.textContent = formatMoney(rawValue);
        });
    }

    applyFormatPrice();
});