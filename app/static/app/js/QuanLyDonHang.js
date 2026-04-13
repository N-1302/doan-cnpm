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
});