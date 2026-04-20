document.addEventListener("DOMContentLoaded", function () {
    console.log("Chi tiết đơn hàng admin đã tải");

    function formatPrice(price) {
        let value = String(price ?? "").trim();

        value = value.replace(/đ|vnd|vnđ/gi, "").trim();

        if (/^\d{1,3}([.,]\d{3})+([.,]\d+)?$/.test(value)) {
            value = value.replace(/[.,](?=\d{3}\b)/g, "");
        }

        value = value.replace(",", ".");

        const number = parseFloat(value);
        return (isNaN(number) ? 0 : number).toLocaleString("vi-VN") + " đ";
    }

    document.querySelectorAll(".money-value").forEach(el => {
        const price = el.getAttribute("data-price");
        el.textContent = formatPrice(price);
    });
});