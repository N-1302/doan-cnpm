document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("searchOrderInput");
    const statusFilter = document.getElementById("statusOrderFilter");
    const rows = document.querySelectorAll("#orderTable tbody tr");

    function filterTable() {
        const keyword = searchInput.value.toLowerCase().trim();
        const status = statusFilter.value.toLowerCase().trim();

        rows.forEach(row => {
            const idCell = row.querySelector(".order-id");
            const userCell = row.querySelector(".order-user");
            const statusCell = row.querySelector(".order-status-cell");

            if (!idCell || !userCell || !statusCell) return;

            const id = idCell.textContent.toLowerCase();
            const user = userCell.textContent.toLowerCase();
            const rowStatus = statusCell.textContent.toLowerCase();

            const matchKeyword = id.includes(keyword) || user.includes(keyword);
            const matchStatus = status === "" || rowStatus.includes(status);

            row.style.display = (matchKeyword && matchStatus) ? "" : "none";
        });
    }

    if (searchInput) searchInput.addEventListener("input", filterTable);
    if (statusFilter) statusFilter.addEventListener("change", filterTable);

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