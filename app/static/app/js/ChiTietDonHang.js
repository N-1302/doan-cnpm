document.addEventListener("DOMContentLoaded", function () {
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
        const priceElements = document.querySelectorAll(".format-price");

        priceElements.forEach(function (el) {
            const rawValue = el.getAttribute("data-price") || el.textContent;
            el.textContent = formatMoney(rawValue);
        });
    }

    function applyJsMoney() {
        const moneyElements = document.querySelectorAll(".js-money");

        moneyElements.forEach(function (el) {
            const rawValue = el.dataset.money || el.getAttribute("data-money") || el.textContent;
            el.textContent = formatMoney(rawValue);
        });
    }

    applyFormatPrice();
    applyJsMoney();
});